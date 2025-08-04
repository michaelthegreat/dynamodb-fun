terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.92"
    }
  }

  required_version = ">= 1.2"
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_dynamodb_table" "test_dynamo_table" {
    name = "test_dynamo_table"
    billing_mode = "PAY_PER_REQUEST"
    hash_key = "test_key"

    attribute {
        name = "test_key"
        type = "S"
    }
}