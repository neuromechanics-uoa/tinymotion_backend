# Create a compute instance for running the backend on
resource "openstack_compute_instance_v2" "compute_instance" {
  name            = "tinymotion-backend-${terraform.workspace}"
  flavor_id       = var.flavor_id
  key_pair        = var.key_pair
  security_groups = ["SSH", "default", "https", "HTTP"]

  block_device {
    uuid = var.image_id
    source_type = "image"
    destination_type = "volume"
    boot_index = 0
    volume_size = var.volume_size
    delete_on_termination = true
  }

  network {
    name = var.tenant_name
  }
}

# Create floating ip
resource "openstack_networking_floatingip_v2" "floating_ip" {
  pool  = "external"
}

# Assign floating ip
resource "openstack_compute_floatingip_associate_v2" "floating_ip_association" {
  floating_ip  = openstack_networking_floatingip_v2.floating_ip.address
  instance_id  = openstack_compute_instance_v2.compute_instance.id
}

# Generate ansible host.ini file
locals {
  host_ini_content = templatefile("${path.module}/templates/host.ini.tpl", {
    backend_floating_ip   = openstack_networking_floatingip_v2.floating_ip.address,
    backend_hostname = "tinymotion-backend-${terraform.workspace}",
    vm_private_key_file = var.key_file,
    ansible_user = var.vm_user
  })
}

resource "local_file" "host_ini" {
  filename = "../host.ini"
  content  = local.host_ini_content
  file_permission = "0644"
}
