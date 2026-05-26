terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# --- S3 Bucket ---
resource "aws_s3_bucket" "analytics" {
  bucket = var.s3_bucket_name
  tags   = var.tags
}

resource "aws_s3_bucket_versioning" "analytics" {
  bucket = aws_s3_bucket.analytics.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "analytics" {
  bucket = aws_s3_bucket.analytics.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Block all public access
resource "aws_s3_bucket_public_access_block" "analytics" {
  bucket                  = aws_s3_bucket.analytics.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# --- Glue Database (used by Athena) ---
resource "aws_glue_catalog_database" "nyc_taxi" {
  name = var.athena_database
}

# --- Glue Crawler to auto-discover schema ---
resource "aws_glue_crawler" "nyc_taxi" {
  name          = "nyc-taxi-crawler"
  role          = aws_iam_role.glue.arn
  database_name = aws_glue_catalog_database.nyc_taxi.name

  s3_target {
    path = "s3://${aws_s3_bucket.analytics.bucket}/processed/"
  }

  tags = var.tags
}

# --- Athena Workgroup ---
resource "aws_athena_workgroup" "analytics" {
  name = "analytics"

  configuration {
    result_configuration {
      output_location = "s3://${aws_s3_bucket.analytics.bucket}/athena-results/"
    }
  }

  tags = var.tags
}

# --- IAM Role for Glue Crawler ---
resource "aws_iam_role" "glue" {
  name = "glue-crawler-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "glue.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "glue_service" {
  role       = aws_iam_role.glue.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

resource "aws_iam_role_policy" "glue_s3" {
  name = "glue-s3-access"
  role = aws_iam_role.glue.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject", "s3:PutObject", "s3:ListBucket"]
      Resource = [
        aws_s3_bucket.analytics.arn,
        "${aws_s3_bucket.analytics.arn}/*"
      ]
    }]
  })
}
