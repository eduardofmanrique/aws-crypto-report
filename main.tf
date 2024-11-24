provider "aws" {
  region = "sa-east-1"
}

resource "aws_s3_bucket" "example" {
  bucket = "aws-crypto-report-example-bucket"
}
