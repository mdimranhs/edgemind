# AWS Deployment Guide

EdgeMind runs as a Docker image in Amazon ECR and an ECS Express Mode service backed by AWS Fargate. The API uses Hugging Face Inference API for cloud Qwen inference.

## Prerequisites

- AWS CLI configured with permission to use ECR, ECS, IAM, CloudFormation, and CloudWatch.
- Docker installed and running.
- A Hugging Face access token.
- An AWS region selected, for example `ap-south-1`.

Verify the AWS session before creating resources:

```bash
aws sts get-caller-identity
```

## Build and push the image

Run these commands from the repository root. Replace the region and account ID with your values.

```bash
export AWS_REGION=ap-south-1
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export ECR_REPOSITORY=edgemind-api
export IMAGE_TAG=$(git rev-parse --short HEAD)
export ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY"

aws ecr describe-repositories --repository-names "$ECR_REPOSITORY" --region "$AWS_REGION" >/dev/null 2>&1 || \
  aws ecr create-repository --repository-name "$ECR_REPOSITORY" --image-scanning-configuration scanOnPush --region "$AWS_REGION"

aws ecr get-login-password --region "$AWS_REGION" | \
  docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

docker build --platform linux/amd64 -t "$ECR_URI:$IMAGE_TAG" .
docker push "$ECR_URI:$IMAGE_TAG"
```

## Create the ECS service

Create an ECS task definition with a container named `Main`, port `8000`, and the ECR image. ECS Express Mode requires a Fargate-compatible task definition. Store `HF_TOKEN` in Secrets Manager or SSM rather than committing it to the repository.

The service health check should use:

```text
/health
```

The image listens on `0.0.0.0:8000`.

After the task definition is registered, create the service with:

```bash
aws ecs create-express-gateway-service \
  --cluster default \
  --task-definition-arn "$TASK_DEFINITION_ARN" \
  --infrastructure-role-arn "$ECS_INFRASTRUCTURE_ROLE_ARN" \
  --health-check-path /health \
  --monitor-resources \
  --region "$AWS_REGION"
```

ECS Express Mode provisions the Fargate service, HTTPS endpoint, load balancer, networking, scaling, and monitoring around the task. Record the generated endpoint and configure the Vercel frontend to use it.

## Environment variables

```text
LLM_PROVIDER=hf_api
HF_MODEL=Qwen/Qwen2.5-1.5B-Instruct
HF_TOKEN=<secret>
DEBUG=false
WEB_SEARCH_ENABLED=true
RAG_LOCAL_FILES_ONLY=true
```

## Current migration boundary

The first deployment keeps SQLite and FAISS inside the container for compatibility with local development. RDS PostgreSQL with `pgvector` and S3 document storage are the next migration steps described in [architecture.md](architecture.md).

## Smoke test

```bash
curl "https://<ecs-endpoint>/health"
```
