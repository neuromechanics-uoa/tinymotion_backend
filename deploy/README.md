# TinyMotion Backend deployment

## Prerequisites

- Account on NeSI RDC
- Install Ansible
- Install Terraform
- Get a duckdns account and create a subdomain to use with each deployment

## Configuration

You will need to downloaded your *clouds.yaml* from NeSI RDC and ensure it is located in *~/.config/openstack/*.

You will need to configure the deployment by setting some environment variables:

```
export TF_VAR_key_pair="KEY_PAIR_NAME"
export TF_VAR_key_file="~/.ssh/location/to/key_pair"
export TF_VAR_vm_user=ubuntu
export AWS_ACCESS_KEY_ID="<EC2_ACCESS_KEY>"
export AWS_SECRET_KEY="<EC2_SECRET_KEY>"
export OS_CLOUD=mycloud
export TF_VAR_openstack_cloud_name=$OS_CLOUD
```

where

- `TF_VAR_key_pair` is the Key Pair name in NeSI RDC
- `TF_VAR_key_file` is the Key Pair location on your local machine
- `TF_VAR_vm_user` is the user for the selected RDC cloud image
- `AWS_ACCESS_KEY_ID` and `AWS_SECRET_KEY` are EC2 credentials created on the RDC, see [Creating and managing EC2 credentials](https://support.cloud.nesi.org.nz/user-guides/create-and-manage-object-storage/creating-and-managing-ec2-credentials-via-cli/) 
- `OS_CLOUD` is the name of the cloud to use from your *~/.config/openstack/clouds.yaml*

The above is the bare minimum configuration required. See file *variables.tf*
to see other available parameters, such as the flavor (size) of the VM and size
of the volume attached to it.

Further configuration is required for Ansible. You should create a yml file named like *vars/<environment_name>.yml*, where *<environment_name>* is the name of the environment you are deploying (*dev* in the example below). Refer to *vars/example.yml* to see which variables should be set. Secrets could be generated using a command like:

```
python3 -c "import secrets; print(secrets.token_urlsafe())"
```

Note: the above yml file contains secrets and should be protected

## Deployment

Run the deployment for the *dev* environment:

```
./deployment.sh create dev
```

If this runs successfully this should bring up the tinymotion service and point your duckdns to the floating IP associated with the VM that was created by terraform.

## TODO

- setup firewall
- separate playbook that updates (including stop swag, remove config, pull and start again - to get new config)
