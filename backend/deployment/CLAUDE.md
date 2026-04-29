# Manual backend deployment

SSH into the EC2 instance:
```
ssh -i ~/.ssh/pilates-gpt-ec2 ec2-user@<elastic-ip>
```

Authenticate Docker to the ECR:
```
aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 127624060144.dkr.ecr.eu-west-2.amazonaws.com
```

Pull the Docker image:
```
docker pull 127624060144.dkr.ecr.eu-west-2.amazonaws.com/pilates:latest
```

## First-time setup

Copy the compose and Caddy config files to the instance (run from the repo root):
```
scp -i ~/.ssh/pilates-gpt-ec2 backend/deployment/docker-compose.yml ec2-user@<elastic-ip>:~/
scp -i ~/.ssh/pilates-gpt-ec2 backend/deployment/Caddyfile ec2-user@<elastic-ip>:~/
```

## Start (or update) the services

```
docker compose up -d
```

Caddy will automatically obtain a Let's Encrypt TLS certificate on first start.
To update the app image after a new push to ECR, re-pull and restart:
```
docker pull 127624060144.dkr.ecr.eu-west-2.amazonaws.com/pilates:latest
docker compose up -d --no-deps pilates
```
