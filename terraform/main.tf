terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

variable "total_instance_count" {
  description = "Total number of instances to create"
  type        = number
  default     = 0
}

resource "aws_security_group" "allow_ssh" {
  name        = "allow_ssh"
  description = "Allow incoming SSH traffic"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "allow_all" {
  name        = "allow_all"
  description = "Allow all traffic"

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "instance_gratuite" {
  count         = var.total_instance_count
  ami           = "ami-04b70fa74e45c3917" # Ubuntu
  instance_type = "t2.large"
  key_name      = "Cle_test_terraform"

  tags = {
    Name = "ubuntu-gratuit-${count.index}"
  }

  vpc_security_group_ids = [
    aws_security_group.allow_ssh.id,
    aws_security_group.allow_all.id
  ]

  provisioner "file" {
    source      = "./scripts/script.sh"
    destination = "/tmp/script.sh"
  }

  provisioner "file" {
    source      = "./scripts/lib/example.dict"
    destination = "/tmp/example.dict"
  }

  provisioner "file" {
    source      = "./scripts/lib/hash.hash"
    destination = "/tmp/hash.hash"
  }

  provisioner "file" {
    source      = "./scripts/lib/hash.hash"
    destination = "/tmp/hash2ash/hash.hash"
  }

  connection {
    type        = "ssh"
    user        = "ubuntu"
    private_key = file("/home/cams/.ssh/Cle_test_terraform.pem")
    host        = self.public_ip
  }

  #lifecycle {
  #  ignore_changes = [ami, instance_type]
  #}
}

output "instances_details" {
  value = [
    for instance in aws_instance.instance_gratuite : {
      public_ip   = instance.public_ip
      name        = lookup(instance.tags, "Name")
      instance_id = instance.id
    }
  ]
}
