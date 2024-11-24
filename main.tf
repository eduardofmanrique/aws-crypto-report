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

resource "random_string" "suffix" {
  length  = 10
  special = false
  upper   = false  # Ensure no uppercase letters
}

resource "aws_s3_bucket" "example" {
  bucket = "my-example-bucket-${lower(random_string.suffix.result)}"
}
