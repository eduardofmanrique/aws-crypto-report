provider "aws" {
  region = "sa-east-1"
}

resource "aws_s3_bucket" "example" {
  bucket = "aws-crypto-report-example-bucket"
}

resource "aws_s3_bucket_versioning" "example" {
  bucket = aws_s3_bucket.example.id

  versioning_configuration {
    status = "Enabled"
  }
}