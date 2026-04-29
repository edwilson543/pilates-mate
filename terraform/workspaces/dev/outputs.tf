output "elastic_ip" {
  value = aws_eip.api.public_ip
}
