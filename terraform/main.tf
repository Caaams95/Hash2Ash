terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  profile = "terraform-user"
  region = "us-east-1"
}

variable "total_instance_count_t2_large" {
  description = "Total number of instances to create"
  type        = number
  default     = 0
}

variable "total_instance_count_c5_xlarge" {
  description = "Total number of instances to create"
  type        = number
  default     = 0
}

variable "total_instance_count_c7a_12xlarge" {
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

# instance_t2_large ==========================================================
resource "aws_instance" "instance_t2_large" {
  count         = var.total_instance_count_t2_large
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
    source      = "./upload_scripts/ssh_commande_start.sh"
    destination = "/tmp/ssh_commande_start.sh"
  }
  provisioner "file" {
    source      = "./upload_scripts/go_hashcat.sh"
    destination = "/tmp/go_hashcat.sh"
  }
  provisioner "file" {
    source      = "./upload_scripts/get_progress.sh"
    destination = "/tmp/get_progress.sh"
  }

    provisioner "file" {
    source      = "./upload_scripts/.env_script"
    destination = "/tmp/.env_script"
  }
    connection {
    type        = "ssh"
    user        = "ubuntu"
    private_key = file("/home/cams/.ssh/Cle_test_terraform.pem")
    host        = self.public_ip
  }
}

# instance_c5_xlarge ==========================================================
resource "aws_instance" "instance_c5_xlarge" {
  count         = var.total_instance_count_c5_xlarge
  ami           = "ami-04b70fa74e45c3917" # Ubuntu
  instance_type = "c5.xlarge"
  key_name      = "Cle_test_terraform"

  tags = {
    Name = "ubuntu-gratuit-${count.index}"
  }

  vpc_security_group_ids = [
    aws_security_group.allow_ssh.id,
    aws_security_group.allow_all.id
  ]
  provisioner "file" {
    source      = "./upload_scripts/ssh_commande_start.sh"
    destination = "/tmp/ssh_commande_start.sh"
  }
  provisioner "file" {
    source      = "./upload_scripts/go_hashcat.sh"
    destination = "/tmp/go_hashcat.sh"
  }
  provisioner "file" {
    source      = "./upload_scripts/get_progress.sh"
    destination = "/tmp/get_progress.sh"
  }
    provisioner "file" {
    source      = "./upload_scripts/.env_script"
    destination = "/tmp/.env_script"
  }
    connection {
    type        = "ssh"
    user        = "ubuntu"
    private_key = file("/home/cams/.ssh/Cle_test_terraform.pem")
    host        = self.public_ip
  }
}


# instance_c7a_12xlarge ==========================================================
resource "aws_instance" "instance_c7a_12xlarge" {
  count         = var.total_instance_count_c7a_12xlarge
  ami           = "ami-04b70fa74e45c3917" # Ubuntu
  instance_type = "c7a.12xlarge"
  key_name      = "Cle_test_terraform"

  tags = {
    Name = "ubuntu-gratuit-${count.index}"
  }

  vpc_security_group_ids = [
    aws_security_group.allow_ssh.id,
    aws_security_group.allow_all.id
  ]
  provisioner "file" {
    source      = "./upload_scripts/ssh_commande_start.sh"
    destination = "/tmp/ssh_commande_start.sh"
  }
    provisioner "file" {
    source      = "./upload_scripts/go_hashcat.sh"
    destination = "/tmp/go_hashcat.sh"
  }
    provisioner "file" {
    source      = "./upload_scripts/get_progress.sh"
    destination = "/tmp/get_progress.sh"
  }

    provisioner "file" {
    source      = "./upload_scripts/.env_script"
    destination = "/tmp/.env_script"
  }
    connection {
    type        = "ssh"
    user        = "ubuntu"
    private_key = file("/home/cams/.ssh/Cle_test_terraform.pem")
    host        = self.public_ip
  }
}

output "instances_details_t2_large" {
  value = [
    for instance in aws_instance.instance_t2_large : {
      public_ip   = instance.public_ip
      name        = lookup(instance.tags, "Name")
      instance_id = instance.id
    }
  ]
}

output "instances_details_c5_xlarge" {
  value = [
    for instance in aws_instance.instance_c5_xlarge : {
      public_ip   = instance.public_ip
      name        = lookup(instance.tags, "Name")
      instance_id = instance.id
    }
  ]
}

output "instances_details_c7a_12xlarge" {
  value = [
    for instance in aws_instance.instance_c7a_12xlarge : {
      public_ip   = instance.public_ip
      name        = lookup(instance.tags, "Name")
      instance_id = instance.id
    }
  ]
}
