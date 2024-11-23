provider "aws" {
  region = "sa-east-1"
}

resource "aws_s3_bucket" "example" {
  bucket = "my-example-bucket-${random_string.suffix.result}"
}

resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false  # Ensures the string is all lowercase
}