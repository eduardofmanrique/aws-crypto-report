provider "aws" {
  region = "sa-east-1"
}

terraform {
  backend "s3" {
    bucket         = "aws-alerts-config-bucket"
    key            = "terraform/state/terraform.tfstate"
    region         = "sa-east-1"
    encrypt        = true
  }
}

# Generate random suffix for the first bucket
resource "random_string" "suffix_1" {
  length  = 10
  special = false
  upper   = false  # Ensure no uppercase letters
}

# Generate random suffix for the second bucket
resource "random_string" "suffix_2" {
  length  = 10
  special = false
  upper   = false  # Ensure no uppercase letters
}

# Create the first S3 bucket
resource "aws_s3_bucket" "example_1" {
  bucket = "my-example-bucket-1-${lower(random_string.suffix_1.result)}"
  acl    = "private"
}

# Create the second S3 bucket
resource "aws_s3_bucket" "example_2" {
  bucket = "my-example-bucket-2-${lower(random_string.suffix_2.result)}"
  acl    = "private"
}


