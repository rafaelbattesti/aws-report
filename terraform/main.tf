////////////////////////////
///// AWS Provider

provider "aws" {
  version                 = ">=1.23.0"
  region                  = "${var.aws_region}"
  profile                 = "${var.aws_profile}"
  shared_credentials_file = "~/.aws/credentials"
}


resource "random_id" "automate-role-hash" {
  byte_length = 4
}

resource "aws_iam_role" "aws_report_role" {
  name = "aws-report-role-${random_id.automate-role-hash.hex}"
  assume_role_policy = <<EOF
{
   "Version": "2012-10-17",
   "Statement": [{
      "Effect": "Allow",
      "Action": [
         "ec2:DescribeInstances", "ec2:DescribeImages",
         "ec2:DescribeTags", "ec2:DescribeSnapshots",
         "ec2:DescribeVolumes"
      ],
      "Resource": "*"
   }
   ]
}
EOF
}

resource "aws_lambda_function" "aws_report_lambda" {
  filename         = "aws-report.zip"
  function_name    = "aws-report-lambda-${random_id.automate-role-hash.hex}"
  role             = "${aws_iam_role.aws_report_role.arn}"
  handler          = "run_lambda.http_server"
  source_code_hash = "${base64sha256(file("aws-report.zip"))}"
  runtime          = "Python3.6"
}