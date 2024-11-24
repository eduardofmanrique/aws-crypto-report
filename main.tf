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

resource "aws_s3_bucket" "example" {
  bucket = "my-example-bucket-${random_string.suffix.result}"
}

resource "random_string" "suffix" {
  length  = 8
  special = false
}