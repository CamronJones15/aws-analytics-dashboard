output "s3_bucket_name" {
  description = "Name of the analytics S3 bucket"
  value       = aws_s3_bucket.analytics.bucket
}

output "athena_workgroup" {
  description = "Athena workgroup name"
  value       = aws_athena_workgroup.analytics.name
}

output "glue_database" {
  description = "Glue catalog database name"
  value       = aws_glue_catalog_database.nyc_taxi.name
}

output "glue_crawler_name" {
  description = "Name of the Glue crawler"
  value       = aws_glue_crawler.nyc_taxi.name
}
