#!/bin/bash -e


scriptname=$0
print_usage() {
    echo "Usage: ${scriptname} <create|destroy> <ENVIRONMENT_NAME>"
    echo
    echo "  - must specify the operation, either \"create\" or \"destroy\""
    echo "  - must specify the environment name, e.g. \"dev\", \"test\", etc."
    echo
}

if [ "$#" -ne 2 ]; then
    print_usage
    exit 1
fi

case $1 in
    "destroy")
        echo "Destroying \"$2\""
        ansible-playbook provision-infrastructure.yml -e operation=destroy -e terraform_workspace=${2:-dev}
        ;;

    "create")
        echo "Creating \"$2\""
        # TODO: need to create workspace in case it doesn't exist

        ansible-playbook provision-infrastructure.yml -e operation=create -e terraform_workspace=${2:-dev}
        ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i host.ini setup-backend.yml \
            -u ${TF_VAR_vm_user} --key-file '${TF_VAR_key_file}' -e terraform_workspace=${2:-dev} \
            -e @vars/${2:-dev}.yml
        ;;

    *)
        print_usage
        exit 1
esac
