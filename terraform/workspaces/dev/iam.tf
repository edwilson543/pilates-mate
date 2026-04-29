# Trust policy, allowing the EC2 instance to assume the `ec2_role`.
data "aws_iam_policy_document" "ec2_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    effect  = "Allow"

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ec2_role" {
  name               = "pilates-gpt-ec2-role"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume_role.json
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "pilates-gpt-ec2-profile"
  role = aws_iam_role.ec2_role.name
}

# Give the EC2 instance ECR read access.
data "aws_iam_policy_document" "ecr_access" {
  statement {
    effect    = "Allow"
    actions   = ["ecr:GetAuthorizationToken"]
    resources = ["*"] # This action is account-level, can't be scoped further
  }

  statement {
    effect = "Allow"
    actions = [
      "ecr:BatchGetImage",
      "ecr:GetDownloadUrlForLayer",
      "ecr:DescribeRepositories",
      "ecr:ListImages",
    ]
    resources = [
      "arn:aws:ecr:eu-west-2:127624060144:repository/pilates"
    ]
  }
}

resource "aws_iam_role_policy" "ecr_access" {
  name   = "ecr-access"
  role   = aws_iam_role.ec2_role.name
  policy = data.aws_iam_policy_document.ecr_access.json
}
