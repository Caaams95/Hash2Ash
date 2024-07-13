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

variable "total_instance_count_low" {
  description = "Total number of instances to create"
  type        = number
  default     = 0
}

variable "total_instance_count_medium" {
  description = "Total number of instances to create"
  type        = number
  default     = 0
}

variable "total_instance_count_high" {
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

# instance_low ==========================================================
resource "aws_instance" "instance_low" {
  count         = var.total_instance_count_low
  ami           = "ami-04b70fa74e45c3917" # Ubuntu
  instance_type = "t2.large"
  key_name      = "Cle_test_terraform"

  tags = {
    Name = "low-instance-${count.index}"
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
    source      = "./upload_scripts/get_progress_live.sh"
    destination = "/tmp/get_progress_live.sh"
  }
  provisioner "file" {
    source      = "./upload_scripts/cost_instance_live.sh"
    destination = "/tmp/cost_instance_live.sh"
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

# instance_medium ==========================================================
resource "aws_instance" "instance_medium" {
  count         = var.total_instance_count_medium
  ami           = "ami-04b70fa74e45c3917" # Ubuntu
  instance_type = "c7a.4xlarge"
  key_name      = "Cle_test_terraform"

  tags = {
    Name = "medium-instance-${count.index}"
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
    source      = "./upload_scripts/get_progress_live.sh"
    destination = "/tmp/get_progress_live.sh"
  }
  provisioner "file" {
    source      = "./upload_scripts/cost_instance_live.sh"
    destination = "/tmp/cost_instance_live.sh"
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


# instance_high ==========================================================
resource "aws_instance" "instance_high" {
  count         = var.total_instance_count_high
  ami           = "ami-04b70fa74e45c3917" # Ubuntu
  instance_type = "c7a.12xlarge"
  key_name      = "Cle_test_terraform"

  tags = {
    Name = "high-instance-${count.index}"
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
    source      = "./upload_scripts/get_progress_live.sh"
    destination = "/tmp/get_progress_live.sh"
  }
  provisioner "file" {
    source      = "./upload_scripts/cost_instance_live.sh"
    destination = "/tmp/cost_instance_live.sh"
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

output "instances_details_low" {
  value = [
    for instance in aws_instance.instance_low : {
      public_ip   = instance.public_ip
      name        = lookup(instance.tags, "Name")
      instance_id = instance.id
    }
  ]
}

output "instances_details_medium" {
  value = [
    for instance in aws_instance.instance_medium : {
      public_ip   = instance.public_ip
      name        = lookup(instance.tags, "Name")
      instance_id = instance.id
    }
  ]
}

output "instances_details_high" {
  value = [
    for instance in aws_instance.instance_high : {
      public_ip   = instance.public_ip
      name        = lookup(instance.tags, "Name")
      instance_id = instance.id
    }
  ]
}
