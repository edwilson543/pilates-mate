The application is deployed on AWS infrastructure and managed by Terraform.
This directory contains the terraform code.

# Terraform structure                                                                                                                                                           
The Terraform code for the backend lives in `./terraform`.                                                                                                                       
At root, the package is organised into:                                                                                                                                          
- Workspaces:                                                                                                                                                                    
  - Each workspace represents an isolated deployment environment                                                                                                                 
  - Each workspace's Terraform state is therefore tracked independently                                                                                                          
  - For example `./terraform/workspaces/prod` contains the production deployment environment                                                                                     
- Modules:                                                                                                                                                                       
  - These contain re-usable collections of Terraform configuration files                                                                                                         
  - For example `./terraform/modules/eks` contains the configuration files for deploying an EKS cluster

TODO: document the AWS services used, Terraform conventions, and the apply pipeline.
