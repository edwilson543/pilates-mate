module "ec2_instance" {
  source  = "terraform-aws-modules/ec2-instance/aws"

  name = "pilates-gpt"
  instance_type = "t3.micro"
  ami_ssm_parameter = "/aws/service/ecs/optimized-ami/amazon-linux-2023/recommended/image_id"

  key_name      = "pilates-gpt-ec2"
  associate_public_ip_address = true
  vpc_security_group_ids = [aws_security_group.api_security_group.id]
  subnet_id = var.subnet_id
  iam_instance_profile = aws_iam_instance_profile.ec2_profile.name

  monitoring    = true

  tags = {
    Terraform   = "true"
    Environment = "dev"
  }
}

resource "aws_security_group" "api_security_group" {
  name = "api-security-group"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["77.98.205.253/32"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_key_pair" "my_key" {
  key_name   = "pilates-gpt-ec2"
  public_key = file("~/.ssh/pilates-gpt-ec2.pub")
}
