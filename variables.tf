variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "s3_bucket_name" {
  description = "Name of the S3 bucket for raw and processed data"
  type        = string
}

variable "athena_database" {
  description = "Glue/Athena database name"
  type        = string
  default     = "nyc_taxi"
}

variable "tags" {
  description = "Tags applied to all resources"
  type        = map(string)
  default = {
    Project     = "aws-analytics-dashboard"
    Environment = "dev"
  }
}
