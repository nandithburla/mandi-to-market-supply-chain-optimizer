# AWS Deployment

This document explains the production deployment of the Mandi-to-Market Supply Chain Optimizer on AWS.

---

## 1. AWS Deployment Architecture

The application uses Amazon ECR for Docker images, Amazon EKS for Kubernetes deployment, and an EC2 instance with Nginx as the public gateway.

```text
                         INTERNET
                            │
                            ▼
                    Elastic IP
                   51.20.97.243
                            │
                            ▼
                    EC2 Gateway
                     t3.micro
                            │
                          Nginx
                            │
                            ▼
                 EKS Worker Node
              192.168.30.138:31324
                            │
                            ▼
                    Kubernetes
                         Service
                            │
                            ▼
                  Application Pods
                            │
                 ┌──────────┴──────────┐
                 ▼                     ▼
          FastAPI Backend       React Frontend
                 │
                 ▼
             SQLite DB
2. AWS Region

The project is deployed in:

Region: eu-north-1
Location: Stockholm

AWS resources used by the project are created in this region.

3. Amazon ECR

Amazon Elastic Container Registry (ECR) is used to store the Docker image of the application.

Repository:

mandi-to-market-optimizer

Registry:

556880009395.dkr.ecr.eu-north-1.amazonaws.com

Complete image format:

[556880009395.dkr.ecr.eu-north-1.amazonaws.com/mandi-to-market-optimizer](https://556880009395.dkr.ecr.eu-north-1.amazonaws.com/mandi-to-market-optimizer):<IMAGE_TAG>

The image tag is based on the Git commit SHA.

Example:

4e7880e28bef901a59696115e5936f7b0d7b0d6a

The basic flow is:

Source Code
     ↓
Docker Build
     ↓
Docker Image
     ↓
Amazon ECR
4. Amazon EKS

The application runs inside an Amazon Elastic Kubernetes Service cluster.

Cluster:

mandi-agent-cluster

Region:

eu-north-1

The cluster uses worker nodes to run the application containers.

Current worker nodes:

Worker Node 1
Public IP: 13.60.62.80
Private IP: 192.168.30.138

Worker Node 2
Public IP: 51.20.127.85
Private IP: 192.168.60.63

The worker nodes are part of the Kubernetes cluster and provide the compute capacity for the application pods.

5. Kubernetes Deployment

The application is deployed using a Kubernetes Deployment.

Deployment name:

mandi-to-market-optimizer

Container name:

mandi-to-market-app

The deployment pulls the Docker image from Amazon ECR.

The Kubernetes deployment manages the application replicas and allows new versions to be rolled out without manually recreating the application.

Basic structure:

EKS Cluster
     ↓
Kubernetes Deployment
     ↓
Application Pods
     ↓
Docker Container
6. Application Pods

The application runs in multiple Kubernetes pods.

Example running pods:

mandi-to-market-optimizer-5fbff468dd-r8f6g
mandi-to-market-optimizer-5fbff468dd-wlhnx

Both pods reached:

1/1 Running

Running multiple replicas provides application availability if one pod becomes unavailable.

7. Kubernetes Service and NodePort

The application is exposed through a Kubernetes NodePort.

NodePort:

31324

The traffic path is:

EC2 Gateway
     ↓
Worker Node
     ↓
NodePort 31324
     ↓
Kubernetes Service
     ↓
Application Pod

The NodePort provides a fixed port through which the EC2 gateway can reach the application running inside EKS.

8. Why NodePort Was Used

The initial deployment attempted to expose the application using an AWS-managed LoadBalancer.

AWS returned:

OperationNotPermitted:
This AWS account currently does not support creating load balancers.

Because the account could not create the required load balancer, the architecture was changed.

Final approach:

Internet
   ↓
EC2
   ↓
Nginx
   ↓
EKS NodePort
   ↓
Application

This allowed the application to remain publicly accessible without depending on an AWS-managed load balancer.

9. EC2 Gateway

An EC2 instance is used as the public gateway.

Configuration:

Instance ID:
i-0867906cb65ad1d08

Instance Type:
t3.micro

Operating System:
Amazon Linux 2023

Private IP:
192.168.32.112

Elastic IP:
51.20.97.243

The EC2 instance does not run the main application.

Its main purpose is to receive public HTTP traffic and forward it to the Kubernetes NodePort using Nginx.

10. Elastic IP

The EC2 gateway uses:

51.20.97.243

as its Elastic IP.

This provides a stable public address for the application.

Therefore, users can access the application using:

[http://51.20.97.243](http://51.20.97.243)

The Elastic IP remains associated with the gateway instead of relying on a changing public IP.

11. Nginx Reverse Proxy

Nginx is installed on the EC2 gateway.

Its purpose is to receive HTTP requests from the internet and forward them to the Kubernetes application.

The current upstream target is:

192.168.30.138:31324

The complete flow is:

Browser
   ↓
[http://51.20.97.243](http://51.20.97.243)
   ↓
EC2
   ↓
Nginx
   ↓
192.168.30.138:31324
   ↓
Kubernetes Service
   ↓
Application Pod

Nginx therefore acts as the reverse proxy between the public internet and the EKS application.

12. Security Groups

The deployment uses AWS security groups to control network traffic.

The EC2 gateway security group allows the required public web traffic and allows communication toward the Kubernetes worker node.

The EKS worker nodes use their own security group for cluster and application traffic.

The important principle is:

Internet
   ↓
EC2 Gateway
   ↓
Allowed internal traffic
   ↓
EKS Worker Node

Only the required ports should be exposed.

13. OpenRouter API Secret

The AI Agricultural Assistant requires an OpenRouter API key.

The key is not stored directly in the source code.

For Kubernetes deployment, the secret is stored as:

openrouter-secret

The application reads the secret at runtime.

This prevents the API credential from being committed to GitHub.

14. Production Deployment Flow

The complete production flow is:

Developer
    ↓
Git Push
    ↓
GitHub Actions
    ↓
Docker Build
    ↓
Amazon ECR
    ↓
Amazon EKS
    ↓
Kubernetes Deployment
    ↓
Application Pods
    ↓
NodePort 31324
    ↓
EC2 Gateway
    ↓
Nginx
    ↓
Elastic IP
    ↓
Public Application

GitHub Actions and OIDC are documented separately in:

docs/GITHUB_ACTIONS.md
15. Updating the Application

When application code changes, the normal process is:

Code Change
    ↓
git add .
    ↓
git commit
    ↓
git push origin main
    ↓
GitHub Actions
    ↓
New Docker Image
    ↓
Amazon ECR
    ↓
EKS Deployment Update
    ↓
Kubernetes Rolling Update

The deployment uses the Git commit SHA as the Docker image tag.

This makes it possible to identify which source-code version is running in production.

16. Connect to the EKS Cluster

To connect kubectl to the cluster:

aws eks update-kubeconfig --region eu-north-1 --name mandi-agent-cluster

Check the worker nodes:

kubectl get nodes

Check application pods:

kubectl get pods -o wide

Check the deployment:

kubectl get deployment mandi-to-market-optimizer

Check the service:

kubectl get service
17. Verify the Deployed Image

To see the Docker image currently configured for the deployment:

kubectl get deployment mandi-to-market-optimizer -o jsonpath="{.spec.template.spec.containers[0].image}"

The image should point to the project's ECR repository and contain the expected Git commit SHA.

18. Check Application Logs

If the application has a problem, check the pod logs:

kubectl logs deployment/mandi-to-market-optimizer

For more detailed deployment information:

kubectl describe deployment mandi-to-market-optimizer
19. Check Nginx

On the EC2 gateway:

sudo systemctl status nginx

Test the Nginx configuration:

sudo nginx -t

Restart Nginx if required:

sudo systemctl restart nginx
20. Production Verification

The final application was verified through the public address:

[http://51.20.97.243](http://51.20.97.243)

The production path is:

Public Internet
      ↓
51.20.97.243
      ↓
EC2 + Nginx
      ↓
192.168.30.138:31324
      ↓
EKS
      ↓
Kubernetes Service
      ↓
Application Pods

The application pods were successfully running after deployment.

21. Final AWS Architecture
                         AWS
                          │
             ┌────────────┴────────────┐
             │                         │
        Amazon ECR                 Amazon EKS
             │                         │
       Docker Image             Kubernetes Deployment
                                       │
                                  Application Pods
                                       │
                                  NodePort 31324
                                       │
                                       ▼
                              EC2 Gateway Instance
                                  t3.micro
                                       │
                                    Nginx
                                       │
                                Elastic IP
                                51.20.97.243
                                       │
                                       ▼
                                  INTERNET

The final deployment combines AWS ECR, EKS, Kubernetes, NodePort, EC2, Nginx, and an Elastic IP to provide a publicly accessible production application.