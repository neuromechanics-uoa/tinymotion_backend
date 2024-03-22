[all]
backend ansible_host=${backend_floating_ip} hostname=${backend_hostname}

[all:vars]
ansible_user=${ansible_user}
vm_private_key_file=${vm_private_key_file}
ansible_ssh_common_args="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
