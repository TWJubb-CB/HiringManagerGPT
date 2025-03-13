variable "aws_region" {
  description = "Static IPv6 address for the instance"
  type        = string
  default     = "eu-west-2"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.micro"
}

variable "ami_id" {
  description = "EC2 AMI "
  type        = string
  default     = "ami-04da26f654d3383cf"
}

variable "elastic_ip_id" {
  description = "Elastic IP ID (get from console)"
  type        = string
}

variable "ec2_keypair_name" {
  description = "Name of the keypair created for use with EC2"
  type        = string
}

variable "conda_env_name" {
  description = "Name of the conda environment"
  type        = string
  default     = "gcp-bq"
}


# Environment variables

variable "OPENAI_API_KEY_NAME" {
  description = "The name of the SSM key"
  type        = string
}

variable "OPENAI_ENC_KEY" {
  description = "The name of the SSM key"
  type        = string
}
