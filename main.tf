provider "aws" {
  region = "sa-east-1"
}

terraform {
  backend "s3" {
    bucket         = "aws-alerts-config-bucket"
    key            = "crypto_report/terraform/state/terraform.tfstate"
    region         = "sa-east-1"
    encrypt        = true
  }
}

resource "aws_iam_role" "lambda_role" {
  name               = "lambda-basic-role-crypto-report"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy_attachment" "lambda_basic_policy" {
  name       = "lambda-basic-policy-attachment"
  roles      = [aws_iam_role.lambda_role.name]
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_layer_version" "dependencies_layer" {
  filename   = "lambda_dependencies.zip"
  layer_name = "lambda-dependencies-crypto-report"
  compatible_runtimes = ["python3.9"]
}

resource "aws_lambda_function" "example" {
  function_name = "lambda-crypto-report"
  role          = aws_iam_role.lambda_role.arn
  handler       = "main.handler"
  runtime       = "python3.9"
  filename      = "lambda.zip"
  source_code_hash = filebase64sha256("lambda.zip")
  timeout       = 120
  memory_size   = 300
  layers        = [
    "arn:aws:lambda:sa-east-1:336392948345:layer:AWSSDKPandas-Python39:29",
    aws_lambda_layer_version.dependencies_layer.arn
  ]
}

resource "aws_iam_policy_attachment" "lambda_sqs_full_access" {
  name       = "lambda-sqs-full-access-attachment"
  roles      = [aws_iam_role.lambda_role.name]
  policy_arn = "arn:aws:iam::aws:policy/AmazonSQSFullAccess"
}

resource "aws_cloudwatch_event_rule" "every_2_minutes" {
  name        = "lambda-trigger-every-2-minutes"
  description = "Trigger Lambda every 2 minutes"
  schedule_expression = "rate(2 minutes)"
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.every_2_minutes.name
  target_id = "lambda-crypto-report-target"
  arn       = aws_lambda_function.example.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_invoke" {
  statement_id  = "AllowCloudWatchInvoke"
  action        = "lambda:InvokeFunction"
  principal     = "events.amazonaws.com"
  function_name = aws_lambda_function.example.function_name
  source_arn    = aws_cloudwatch_event_rule.every_2_minutes.arn
}
