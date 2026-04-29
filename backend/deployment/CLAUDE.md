# Manual backend deployment
SSH into the EC2 instance:
```
ssh -i ~/.ssh/pilates-gpt-ec2 ec2-user@<public-ip>
```

Authenticate Docker to the ECR:
```
aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 127624060144.dkr.ecr.eu-west-2.amazonaws.com
```

Pull the Docker image in the container:
```
docker pull 127624060144.dkr.ecr.eu-west-2.amazonaws.com
```

Run the container:
```
docker container run -d -p 80:8000 --rm --name=pilates pilates:latest api
```
