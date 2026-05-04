# Deployment configuration
The backend API is simply deployed by running the `docker-compose.yml` file in this directory on a solitary
EC2 instance.

# Deployment process
## Manual
Get the EC2 instance's public IP:
```bash
export EC2_IP=$(aws ec2 describe-instances --filters "Name=tag:Name,Values=pilates-gpt" --query "Reservations[*].Instances[*].PublicIpAddress" --output text)
```

Push the latest image to ECR:
```bash
make ecr_push
```

Copy across the deployment files (if there have been any updates):
```bash
scp -i ~/.ssh/pilates-gpt-ec2 backend/deployment/.env.dev ec2-user@${EC2_IP}:~/.env
scp -i ~/.ssh/pilates-gpt-ec2 backend/deployment/docker-compose.yml ec2-user@${EC2_IP}:~/
scp -i ~/.ssh/pilates-gpt-ec2 backend/deployment/Caddyfile ec2-user@${EC2_IP}:~/
```

SSH into the EC2 instance and restart the containers:
```bash
ssh -i ~/.ssh/pilates-gpt-ec2 ec2-user@${EC2_IP}
```

Restart the Docker containers:
```bash
aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 127624060144.dkr.ecr.eu-west-2.amazonaws.com
docker pull 127624060144.dkr.ecr.eu-west-2.amazonaws.com/pilates:latest
docker-compose up -d
```
