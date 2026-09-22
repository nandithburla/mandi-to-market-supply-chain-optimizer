# Errors and Solutions

This document records the main problems encountered while deploying the Mandi-to-Market Supply Chain Optimizer and how they were resolved.

---

## 1. AWS Load Balancer Creation Failed

### Error

While trying to expose the Kubernetes application using an AWS LoadBalancer, AWS returned:

```text
OperationNotPermitted:
This AWS account currently does not support creating load balancers.

Why It Happened
The AWS account did not support creating the required load balancer.

Solution
The deployment architecture was changed to use an EC2 gateway with Nginx and a Kubernetes NodePort.

Internet
   ↓
EC2 + Elastic IP
   ↓
Nginx
   ↓
EKS NodePort
   ↓
Application

Result
The application became publicly accessible without requiring an AWS-managed load balancer.
2. Public Application Could Not Be Exposed Directly
Problem
The application was running inside EKS, but there was no supported AWS LoadBalancer available to provide public access.

Solution
An EC2 instance was created as a public gateway.
Configuration:

EC2 Type: t3.micro
Elastic IP: 51.20.97.243

Nginx on the EC2 instance forwards requests to:

192.168.30.138:31324


Final Flow
Browser
   ↓
51.20.97.243
   ↓
EC2
   ↓
Nginx
   ↓
EKS NodePort 31324
   ↓
Application Pod

3. EC2 Gateway SSH Access Issue
Problem
The initial EC2 gateway setup did not have the required SSH key configuration.

Solution
The gateway was recreated with the key pair:

mandi-gateway-key


This provided SSH access for configuring Nginx and troubleshooting the gateway.
4. NodePort Connectivity Problem
Problem
The application was running inside EKS, but the EC2 gateway needed a reachable worker-node address and port.

Solution
The application was exposed using:

NodePort: 31324


Nginx was configured to forward traffic to:

192.168.30.138:31324


Verification
Check the Kubernetes service:


kubectl get service


Check the application pods:


kubectl get pods -o wide


If the pods are running and the service is configured correctly, the next component to check is Nginx.
5. GitHub Actions Could Not Authenticate with AWS
Error
The GitHub Actions workflow initially failed while trying to assume the AWS IAM role using OIDC.

Why It Happened
The GitHub OIDC trust policy was using an older repository subject format.
The repository was created after GitHub introduced the newer immutable repository identifiers.

Solution
The IAM trust policy was updated to use the repository's immutable identifiers.
The final trusted subject is:

repo:nandithburla@150075721/mandi-to-market-supply-chain-optimizer@1380472620:ref:refs/heads/main


The trust policy also checks:

aud = sts.amazonaws.com


Result
GitHub Actions could successfully assume:

GitHubActions-MandiDeploy


and receive temporary AWS credentials.
6. GitHub Actions Secrets Were Missing
Problem
The deployment workflow required AWS role and ECR configuration values.

Solution
The following GitHub repository secrets were configured:

AWS_GITHUB_ACTIONS_ROLE_ARN
ECR_REGISTRY

The workflow accesses them using:


${{ secrets.SECRET_NAME }}


Permanent AWS access keys are not required.
7. GitHub Actions Did Not Have EKS Access
Problem
AWS authentication succeeded, but the GitHub Actions role still needed permission to interact with the EKS cluster.

Solution
An EKS access entry was created for:

GitHubActions-MandiDeploy


The role was associated with:

AmazonEKSEditPolicy


for the required namespace.

Result
GitHub Actions could run commands such as:


kubectl set image ...
kubectl rollout status ...

against the EKS cluster.
8. Kubernetes Container Name Mismatch
Problem
The GitHub Actions workflow attempted to update a Kubernetes container using the wrong container name.
The actual container name in the deployment is:

mandi-to-market-app


Why It Happened
The deployment name and container name are different:

Deployment:
mandi-to-market-optimizer

Container:
mandi-to-market-app

Both names must be used correctly.

Solution
The workflow was changed to:


kubectl set image deployment/mandi-to-market-optimizer \
  mandi-to-market-app=$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG

Result
The workflow successfully updated the application image.
9. Docker Image Version Identification
Problem
Using a generic Docker tag such as latest makes it difficult to know exactly which source-code version is running.

Solution
The GitHub commit SHA is used as the Docker image tag.
Example:

4e7880e28bef901a59696115e5936f7b0d7b0d6a


This creates a clear relationship:

Git Commit
    ↓
Docker Image
    ↓
ECR
    ↓
Kubernetes Deployment

Benefit
A deployed image can be traced back to the exact Git commit that created it.
10. Kubernetes Deployment Rollout
Problem
Updating the Kubernetes image does not automatically prove that the new pods started successfully.

Solution
The GitHub Actions workflow waits for the rollout:


kubectl rollout status deployment/mandi-to-market-optimizer --timeout=5m


Verification
Check the pods manually:


kubectl get pods


A healthy pod should show:

1/1 Running


11. OpenRouter API Key Security
Problem
The AI Agricultural Assistant requires an OpenRouter API key.
Putting the key directly inside source code could expose the credential.

Solution
The key is provided through a secure secret mechanism.
Kubernetes secret:

openrouter-secret


The actual API key is not stored in the source code or documentation.

Important
Never commit:

API keys
AWS secret keys
Passwords
Private credentials

to GitHub.
12. Application Not Working After Deployment
When the public application is not responding, the problem should be checked from the inside outward.

Troubleshooting Order
1. Application Pod
        ↓
2. Kubernetes Deployment
        ↓
3. Kubernetes Service
        ↓
4. NodePort
        ↓
5. EC2 Gateway
        ↓
6. Nginx
        ↓
7. Elastic IP
        ↓
8. Browser

Useful Commands
Check pods:


kubectl get pods -o wide


Check deployment:


kubectl get deployment mandi-to-market-optimizer


Check service:


kubectl get service


Check logs:


kubectl logs deployment/mandi-to-market-optimizer


Check Nginx:


sudo systemctl status nginx


Test Nginx configuration:


sudo nginx -t


13. Unused Elastic IPs
Problem
During the earlier load-balancer attempts, additional Elastic IPs were allocated.
Unused AWS resources can create unnecessary costs.

Addresses from the abandoned setup
13.53.64.213
13.63.250.7
56.228.73.226

These were associated with the earlier load-balancer attempt.
The NAT gateway Elastic IP:

13.62.253.223


is in use and should not be released.
14. GitHub Actions Warnings
Problem
GitHub Actions can display warnings related to runner images, action runtimes, or future platform changes.

Important
A warning does not necessarily mean that deployment failed.
The important checks are:

GitHub Actions → Success
        ↓
Docker Image → Pushed
        ↓
Kubernetes Rollout → Successful
        ↓
Pods → Running
        ↓
Public Application → Accessible

The workflow uses maintained actions such as:

actions/checkout@v4
aws-actions/configure-aws-credentials@v4
aws-actions/amazon-ecr-login@v2

15. Final Working Deployment
After resolving the deployment issues, the final architecture became:

GitHub
   ↓
GitHub Actions
   ↓
AWS OIDC
   ↓
Amazon ECR
   ↓
Amazon EKS
   ↓
Kubernetes Pods
   ↓
NodePort 31324
   ↓
EC2 Gateway
   ↓
Nginx
   ↓
Elastic IP
51.20.97.243
   ↓
Public Application

The application was successfully deployed and verified at:

[http://51.20.97.243](http://51.20.97.243)


The main lesson from the deployment was to troubleshoot the system layer by layer rather than changing multiple components at once.