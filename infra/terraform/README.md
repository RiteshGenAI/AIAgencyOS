# AI Agency OS — AWS Production Infrastructure

This Terraform template provisions a production-ready AWS environment for AI Agency OS.

## What is deployed

- **VPC** with public and private subnets across two AZs, NAT gateways, and an Internet gateway.
- **Application Load Balancer** (ALB) routing `/api/*`, `/healthz`, and `/health` to the backend, and all other traffic to the frontend.
- **ECS Fargate** services for backend, agents, and frontend.
- **RDS PostgreSQL 16** in private subnets with encryption, backups, and multi-AZ in production.
- **ECR** repositories with image scanning enabled for all services.
- **Secrets Manager** for the database URL and backend JWT secret key.
- **S3** artifacts bucket with encryption, versioning, and public access blocked.
- **IAM** roles and policies with least-privilege access.

## Prerequisites

- AWS CLI installed and configured with credentials.
- Terraform >= 1.5.0 installed.
- Docker installed (for building and pushing images).

## Quick start

1. **Generate a strong backend secret key:**

   ```bash
   export BACKEND_SECRET_KEY=$(openssl rand -hex 32)
   ```

2. **Initialize Terraform:**

   ```bash
   cd infra/terraform
   terraform init
   ```

3. **Plan and apply:**

   ```bash
   terraform plan -var="backend_secret_key=$BACKEND_SECRET_KEY" -out=tfplan
   terraform apply tfplan
   ```

4. **Build and push Docker images:**

   After `terraform apply`, use the ECR repository URLs from the outputs. The production images are built from the inline Dockerfiles in `docker-compose.yml`:

   ```bash
   export AWS_REGION=us-east-1
   export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
   export BACKEND_SECRET_KEY=$(openssl rand -hex 32)

   aws ecr get-login-password --region $AWS_REGION | \
     docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

   # Build the production images using the inline Dockerfiles in docker-compose.yml
   docker compose build

   # Tag and push to ECR
   docker tag ai-agency-os-backend:latest  $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$(terraform output -raw ecr_backend_repository_url):latest
   docker tag ai-agency-os-agents:latest   $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$(terraform output -raw ecr_agents_repository_url):latest
   docker tag ai-agency-os-frontend:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$(terraform output -raw ecr_frontend_repository_url):latest

   docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$(terraform output -raw ecr_backend_repository_url):latest
   docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$(terraform output -raw ecr_agents_repository_url):latest
   docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$(terraform output -raw ecr_frontend_repository_url):latest
   ```

   > **Note:** `docker compose build` evaluates the compose file. You must set `BACKEND_SECRET_KEY` even for builds because the production compose requires it at parse time. Use any value for builds; the actual runtime secret is pulled from AWS Secrets Manager on ECS.

5. **Access the application:**

   Open the ALB DNS name from the Terraform outputs in your browser:

   ```bash
   terraform output alb_dns_name
   ```

## Configuration

Key variables are defined in `variables.tf`. Common overrides:

| Variable | Description | Default |
|----------|-------------|---------|
| `aws_region` | AWS region | `us-east-1` |
| `environment` | Environment name | `prod` |
| `backend_secret_key` | JWT secret key | required |
| `db_instance_class` | RDS instance class | `db.t3.micro` |
| `llm_provider` | LLM provider for agents | `ollama` |
| `llm_model` | LLM model name | `llama3.2` |
| `llm_base_url` | LLM provider base URL | `""` |
| `llm_api_key` | LLM provider API key | `""` |
| `allowed_cidr` | CIDR allowed to access the ALB | `0.0.0.0/0` |

Example with Ollama on an external host:

```bash
terraform apply -var="backend_secret_key=$BACKEND_SECRET_KEY" \
                -var="llm_provider=ollama" \
                -var="llm_model=llama3.2" \
                -var="llm_base_url=http://ollama.example.com:11434"
```

Example with OpenAI:

```bash
terraform apply -var="backend_secret_key=$BACKEND_SECRET_KEY" \
                -var="llm_provider=openai" \
                -var="llm_model=gpt-4o-mini" \
                -var="llm_api_key=$OPENAI_API_KEY"
```

## Security notes

- The backend JWT secret key is stored in AWS Secrets Manager and never logged.
- The RDS master password is generated randomly and stored in Secrets Manager.
- RDS is not publicly accessible and lives in private subnets.
- ECS tasks run in private subnets; only the ALB is public.
- S3 bucket has public access blocked, encryption, and versioning enabled.
- ECR repositories have image scanning enabled on push.
- No hardcoded secrets exist in the Terraform files.

## Cleanup

To destroy all resources:

```bash
terraform destroy -var="backend_secret_key=$BACKEND_SECRET_KEY"
```

> **Warning:** This will delete the RDS database and S3 bucket contents (if not empty).
