# GitHub Actions

## Overview

GitHub Actions is used to automatically build and deploy the application whenever changes are pushed to the `main` branch.

```text
Git Push
   ↓
GitHub Actions
   ↓
AWS OIDC
   ↓
Amazon ECR
   ↓
Amazon EKS
   ↓
Kubernetes Rollout

1. Workflow File
The workflow is located at:

.github/workflows/deploy.yml


It runs when code is pushed to:

main


The workflow is named:

Deploy Mandi-to-Market


2. AWS Authentication
The workflow uses GitHub OpenID Connect (OIDC) instead of storing permanent AWS access keys.
The IAM role is:

GitHubActions-MandiDeploy


Role ARN:

arn:aws:iam::556880009395:role/GitHubActions-MandiDeploy


Authentication flow:

GitHub Actions
      ↓
GitHub OIDC
      ↓
AWS STS
      ↓
IAM Role
      ↓
Temporary AWS Credentials

This allows GitHub Actions to securely access AWS resources.
3. GitHub Secrets
The repository contains:

AWS_GITHUB_ACTIONS_ROLE_ARN
ECR_REGISTRY

The ECR registry is:

556880009395.dkr.ecr.eu-north-1.amazonaws.com


The workflow reads these values using GitHub Secrets.
No permanent AWS access keys are stored in the repository.
4. Docker Build and ECR
After checking out the code, GitHub Actions:


Authenticates with AWS.

Logs in to Amazon ECR.

Builds the Docker image.

Pushes the image to ECR.
The image is tagged using:

github.sha


Example:

[556880009395.dkr.ecr.eu-north-1.amazonaws.com/mandi-to-market-optimizer](https://556880009395.dkr.ecr.eu-north-1.amazonaws.com/mandi-to-market-optimizer):<commit-sha>


Using the commit SHA makes each deployment traceable to a specific Git commit.
5. Deploy to EKS
After pushing the image, GitHub Actions connects to:

mandi-agent-cluster


It then updates:

Deployment:
mandi-to-market-optimizer

Container:
mandi-to-market-app

The deployment command is:


kubectl set image deployment/mandi-to-market-optimizer \
  mandi-to-market-app=$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG

6. Rollout Verification
After updating the image, the workflow waits for Kubernetes to complete the rollout:


kubectl rollout status deployment/mandi-to-market-optimizer --timeout=5m


This ensures the GitHub Actions job does not finish successfully until the Kubernetes deployment has completed.
7. Complete CI/CD Flow
Developer
    ↓
git add .
    ↓
git commit
    ↓
git push origin main
    ↓
GitHub Actions
    ↓
Checkout Code
    ↓
Authenticate with AWS OIDC
    ↓
Login to ECR
    ↓
Build Docker Image
    ↓
Push Image to ECR
    ↓
Connect to EKS
    ↓
Update Kubernetes Image
    ↓
Rollout Verification
    ↓
New Application Version Running

8. EKS Permissions
The GitHub Actions IAM role has access required for:


Amazon ECR

Amazon EKS
The main policies are:

GitHubActions-MandiECRPush
GitHubActions-MandiEKSAccess

The role was also added to the EKS cluster through an EKS access entry.
9. Important Configuration
The workflow uses:

AWS Region:
eu-north-1

ECR Repository:
mandi-to-market-optimizer

EKS Cluster:
mandi-agent-cluster

Deployment:
mandi-to-market-optimizer

Container:
mandi-to-market-app

The container name in the workflow must exactly match the container name in the Kubernetes deployment.
10. Successful Deployment
The automated pipeline successfully deployed the application to EKS.
Example deployed image:

[556880009395.dkr.ecr.eu-north-1.amazonaws.com/mandi-to-market-optimizer:4e7880e28bef901a59696115e5936f7b0d7b0d6a](https://556880009395.dkr.ecr.eu-north-1.amazonaws.com/mandi-to-market-optimizer:4e7880e28bef901a59696115e5936f7b0d7b0d6a)


The Kubernetes pods reached:

1/1 Running


The public application is available through the AWS deployment described in:

docs/AWS_DEPLOYMENT.md


Result
With GitHub Actions, the deployment process is automated:

Code Change
    ↓
Git Push
    ↓
Docker Build
    ↓
ECR
    ↓
EKS
    ↓
Kubernetes Rollout

No manual Docker image upload or manual application redeployment is required.