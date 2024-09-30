# TinyMotion Backend deployment

## Prerequisites

- Account on NeSI RDC
- Install Ansible and the *infisical-python* Python package, e.g.:
  ```
  python -m venv venv
  source venv/bin/activate
  pip install ansible infisical-python
  ```
- Install Terraform
- [Inifisical secrets manangement](https://infisical.com/)
- [Optional] Get a duckdns account and create a subdomain to use with each deployment

## Configuration

Configuration and secrets need to be set in infisical.

The following secrets need to be defined:

- `tinymotion_backend/ansible`
  - `AWS_ACCESS_KEY_ID` - EC2 credentials created on the RDC, see [Creating and managing EC2 credentials](https://support.cloud.nesi.org.nz/user-guides/create-and-manage-object-storage/creating-and-managing-ec2-credentials-via-cli/)
  - `AWS_SECRET_KEY` - EC2 credentials created on the RDC, see [Creating and managing EC2 credentials](https://support.cloud.nesi.org.nz/user-guides/create-and-manage-object-storage/creating-and-managing-ec2-credentials-via-cli/)
  - `DUCKDNS_DOMAIN` - required if `duckdns: true` in the ansible deployment (see below)
  - `DUCKDNS_TOKEN` - required if `duckdns: true` in the ansible deployment (see below)
  - `INFISICAL_CLIENT_ID` - infisical machine identity that is to be used to launch the tinymotion backend app
  - `INFISICAL_CLIENT_SECRET` - infisical machine identity that is to be used to launch the tinymotion backend app
  - `INFISICAL_PROJECT_ID` - infisical project id
  - `OS_APPLICATION_CREDENTIAL_ID` - openstack credentials
  - `OS_APPLICATION_CREDENTIAL_SECRET` - openstack credentials
  - `OS_AUTH_URL`
  - `OS_REGION_NAME`
  - `OS_TENANT_NAME`
  - `TINYMOTION_URL`
- `tinymotion_backend/app`
  - `TINYMOTION_ACCESS_TOKEN_SECRET_KEY`
  - `TINYMOTION_REFRESH_TOKEN_SECRET_KEY`
  - `TINYMOTION_DATABASE_SECRET_KEY`
  - `TINYMOTION_VIDEO_SECRET_KEY`

The secrets `TINYMOTION_ACCESS_TOKEN_SECRET_KEY`, `TINYMOTION_REFRESH_TOKEN_SECRET_KEY` and `TINYMOTION_DATABASE_SECRET_KEY` could be generated using a command like:

```
python3 -c "import secrets; print(secrets.token_urlsafe())"
```

The `TINYMOTION_VIDEO_SECRET_KEY` should be generated using:

```
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode('ascii'))"
```

In the environment you are running the deployment from (local machine, GitHub Actions, etc) the
following environment variables need to be set:

- `INFISICAL_PROJECT_ID` - project ID for the project in infisical
- `INFISICAL_CLIENT_ID` - client ID for the machine identity to authenticate as
- `INFISICAL_CLIENT_SECRET` - client secret for the machine identity to authenticate as

Further configuration is required for Ansible. You should create a yml file named like *vars/<environment_name>.yml*, where *<environment_name>* is the name of the environment you are deploying (*dev* in the example below). Refer to *vars/example.yml* to see which variables should be set.

## Deployment

### Duckdns single step deployment

This section only applies if you are using duckdns and have set `duckdns: true` in the yaml config file and have set `DUCKDNS_TOKEN` and `DUCKDNS_DOMAIN` in infisical.

Run the deployment for the *dev* environment:

```
./deployment.sh create dev
```

If this runs successfully this should bring up the tinymotion service and point your duckdns domain to the floating IP associated with the VM that was created by terraform.

### Two step deployment

If you are not using duckdns then this section applies.

First, provision the infrastructure (create VMs, floating IPs, etc) for the *dev* environment:

```
./deployment.sh provision dev
```

Look in the *host.ini* file that should have been created if the above command was successful.
Locate the IP address of the instance in that file, it should be shown as `ansible_host=XXX.X.XXX.XXX`.
Update your DNS settings to point the chosen domain name (`TINYMOTION_URL` in infisical) to point to the IP address from the *host.ini* file.

Once the DNS change has propagated, setup the infrastructure (install docker, etc) for the dev environment:

```
./deployment.sh setup dev
```

## TODO

- setup firewall
- separate playbook that updates (including stop swag, remove config, pull and start again - to get new config)
