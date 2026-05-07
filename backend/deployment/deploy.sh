#!/usr/bin/env bash
set -euo pipefail

SSH_KEY=~/.ssh/pilates-gpt-ec2
ECR_REGISTRY=127624060144.dkr.ecr.eu-west-2.amazonaws.com

EC2_IP=$(aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=pilates-gpt" \
  --query "Reservations[*].Instances[*].PublicIpAddress" \
  --output text)

echo "Deploying to EC2 at ${EC2_IP}..."

scp -i "${SSH_KEY}" deployment/.env.dev ec2-user@"${EC2_IP}":~/.env
scp -i "${SSH_KEY}" deployment/docker-compose.yml ec2-user@"${EC2_IP}":~/
scp -i "${SSH_KEY}" deployment/Caddyfile ec2-user@"${EC2_IP}":~/

echo "Deployment configuration files were copied onto EC2 instance."

ssh -i "${SSH_KEY}" ec2-user@"${EC2_IP}" << EOF
  sudo mkdir -p /usr/local/lib/docker/cli-plugins
  sudo curl -fsSL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64" \
    -o /usr/local/lib/docker/cli-plugins/docker-compose
  sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
  aws ecr get-login-password --region eu-west-2 \
    | docker login --username AWS --password-stdin ${ECR_REGISTRY}
  docker pull ${ECR_REGISTRY}/pilates:latest
  docker compose up -d
EOF

echo "Deploy complete."
