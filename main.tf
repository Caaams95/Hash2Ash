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

variable "instance_count" {
  description = "Number of instances to create"
}

variable "script_path" {
  description = "File to upload"
}

# SSH rule
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
  description = "Allow all trafic"

  // Règle permettant les connexions sortantes vers toutes les destinations et tous les ports
  egress {
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    cidr_blocks     = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "instance-gratuite" {
  count         = var.instance_count
  ami           = "ami-04b70fa74e45c3917" // Ubuntu
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
    source      = var.script_path
    destination = "/tmp/script.sh"
  }

#TEST====================
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

# EXE on boot=======================
  provisioner "remote-exec" {
    inline = [
      "sudo apt-get update -y && sudo apt-get upgrade -y",  # Update (obligatoire pour trouver le repo hashcat)sudo apt install postgresql
      "sudo apt install postgresql -y",
      "sudo apt-get install hashcat -y",  # Install Hashcat
      "chmod +x /tmp/script.sh",  # Assurez-vous que le script est exécutable
      "/tmp/script.sh",  # Exécutez le script
    ]
  }

  connection {
    type        = "ssh"
    //user        = "ec2-user"
    user        = "ubuntu"
    private_key = file("/home/cams/.ssh/Cle_test_terraform.pem")
    host        = self.public_ip
  }

  lifecycle {
    create_before_destroy = true
  }
}

//output "new_instance_public_ips" {
 // value = [for instance in aws_instance.instance-gratuite : instance.public_ip]
#}
output "instances_details" {
  value = [
    for instance in aws_instance.instance-gratuite : {
      public_ip = instance.public_ip
      name      = lookup(instance.tags, "Name")
    }
  ]
}