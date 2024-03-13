#!/bin/bash -e

case $1 in
    "destroy")
        ansible-playbook provision-infrastructure.yml -e operation=destroy -e terraform_workspace=${2:-test}
        ;;

    "create")
        ansible-playbook provision-infrastructure.yml -e operation=create -e terraform_workspace=${2:-test}
        ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i host.ini setup-backend.yml \
            -u ${TF_VAR_vm_user} --key-file '${TF_VAR_key_file}' -e terraform_workspace=${2:-test}
        ;;

    *)
        echo "Usage: ${0} <create|destroy> [ENVIRONMENT_NAME]"
        echo
        echo "  - must specify the operation, either \"create\" or \"destroy\""
        echo "  - optionally pass an environment name, which will default to \"test\""
        echo
        exit 1
esac
