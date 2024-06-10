variable "tenant_name" {
  description = "FlexiHPC project Name"
  default = "AUGMENT-General"
}

variable "auth_url" {
  description = "FlexiHPC authentication URL"
  default = "https://keystone.akl-1.cloud.nesi.org.nz/v3"
}

variable "region" {
  description = "FlexiHPC region"
  default = "akl-1"
}

variable "key_pair" {
  description = "FlexiHPC SSH Key Pair name"
}

variable "key_file" {
  description = "Path to local SSH private key associated with Flexi key_pair, used for provisioning"
}

variable "flavor_id" {
  description = "FlexiHPC Flavor ID, Defaults to balanced1.2cpu4ram"
  default     = "6b2e76a8-cce0-4175-8160-76e2525d3d3d"
}

variable "image_id" {
  description = "FlexiHPC Image ID, Defaults to NeSI-FlexiHPC-Ubuntu-Jammy_22.04"
  default     = "ee420ef7-8baa-4a7d-adf1-2fde47f58fa5" 
}

variable "volume_size" {
  description = "The size of the volume in gigabytes, defaults to 30"
  default     = "30"
}

variable "vm_user" {
  description = "FlexiHPC VM user"
  default = "ubuntu"
}
