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
# Dynamodb resources
resource "aws_dynamodb_table" "test_dynamo_table" {
    name = "test_dynamo_table"
    billing_mode = "PAY_PER_REQUEST"
    hash_key = "test_key"

    attribute {
        name = "test_key"
        type = "S"
    }
}
resource "aws_iam_role" "lambda_role" {
  name = "lambda_web_adapter_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect    = "Allow",
      Principal = { Service = "lambda.amazonaws.com" },
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic_exec" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# resource "aws_lambda_layer_version" "web_adapter_layer" {
#   layer_name          = "AWSLambdaWebAdapter"
#   compatible_runtimes = ["python3.7"]

#   # Download the Lambda Web Adapter zip from GitHub and point to it here
#   filename = "lambda-adapter.zip"
# }

resource "aws_lambda_function" "web_adapter_lambda" {
  function_name = "py37-stream-json"
  handler       = "run.sh"
  runtime       = "python3.12"
  role          = aws_iam_role.lambda_role.arn
  architectures = ["arm64"]

  timeout     = 60
  memory_size = 1024

  filename         = "lambda.zip"
  source_code_hash = filebase64sha256("lambda.zip")

  environment {
    variables = {
      AWS_LWA_INVOKE_MODE      = "response_stream"
      AWS_LAMBDA_EXEC_WRAPPER  = "/opt/bootstrap"
      PORT = "8000"
    }
  }

  layers = [
    # aws_lambda_layer_version.web_adapter_layer.arn
    "arn:aws:lambda:us-east-1:753240598075:layer:LambdaAdapterLayerArm64:24"
  ]
}

resource "aws_lambda_function_url" "lambda_url" {
  function_name      = aws_lambda_function.web_adapter_lambda.function_name
  authorization_type = "NONE"
  invoke_mode        = "RESPONSE_STREAM"

  cors {
    allow_origins = ["*"]
    allow_methods = ["GET"]
  }
}

output "function_url" {
  value = aws_lambda_function_url.lambda_url.function_url
}