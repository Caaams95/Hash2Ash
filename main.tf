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


resource "aws_instance" "instance-gratuite" {
  count         = var.instance_count
  ami           = "ami-04e5276ebb8451442"
  instance_type = "t2.micro"
  key_name      = "Cle_test_terraform"

  tags = {
    Name = "TestInstance-${count.index + 1}"
  }

  vpc_security_group_ids = [aws_security_group.allow_ssh.id]


    # Transfert du dossier /hashcat-master sur chaque instance
  provisioner "file" {
    source      = "./hashcat-master"
    destination = "/tmp/hashcat-master"
  }

    provisioner "file" {
    source      = var.script_path
    destination = "/tmp/script.sh"
  }

  provisioner "remote-exec" {
    inline = [
      "chmod +x /tmp/script.sh",  # Assurez-vous que le script est exécutable
      "/tmp/script.sh",  # Exécutez le script
      "ls / > /tmp/ls.txt",
    ]
  }

  connection {
    type        = "ssh"
    user        = "ec2-user"
    private_key = file("/home/cams/.ssh/Cle_test_terraform.pem")
    host        = self.public_ip
  }

  lifecycle {
    create_before_destroy = true
  }
}

output "new_instance_public_ips" {
  value = [for instance in aws_instance.instance-gratuite : instance.public_ip]
}
