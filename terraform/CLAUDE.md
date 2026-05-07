# Overview
This package contains the terraform configuration to deploy the Pilates backend.
This consists primarily of a solitary EC2 instance, with read access to the ECR
repo where we push the Docker image.

# Development commands
`make fmt` - to format the terraform code
`make lint` - to lint the terraform code
