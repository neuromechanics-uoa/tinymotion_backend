# TinyMotion Backend deployment

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

## Deployment

Run the deployment for the *dev* environment:

```
./deployment.sh create dev
```

After that completes successfully, SSH into the node (IP address in *host.ini*) and run:

```
cd tinymotion_backend
cp .env.example .env

# edit .env appropriately

# get a personal access token from github and store as CR_PAT
echo $CR_PAT | sudo docker login ghcr.io -u USERNAME --password-stdin

# pull the images
sudo docker compose pull

# run the services
sudo docker compose up -d

# check the status
sudo docker compose ps

# check the swag logs
sudo docker compose logs -tf swag

# check the tinymotion logs
sudo docker compose logs -tf tinymotion

# check the tinymotion cli is working
sudo docker compose exec tinymotion tinymotion-backend --help
```

## TODO

- not sure why we need to authenticate with github to pull the images
