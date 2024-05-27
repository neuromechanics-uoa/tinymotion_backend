#!/bin/bash -e


scriptname=$0
print_usage() {
    echo "Usage: ${scriptname} <provision|setup|create|destroy> <ENVIRONMENT_NAME>"
    echo
    echo "  - must specify the operation, either \"create\", \"destroy\", \"provision\" or \"setup\""
    echo "  - must specify the environment name, e.g. \"dev\", \"test\", etc."
    echo
    echo "Operations:"
    echo "  - \"provision\" will provision the infrastructure (VM, floating IP, etc)"
    echo "  - \"setup\" will configure the infrastrucre (install docker, etc) - you must \"provision\" first"
    echo "  - \"create\" runs both \"provision\" and \"setup\" in a single step (suitable only if using duckdns)"
    echo "  - \"destroy\" destroys the infrastructure (VM, floating IP, etc)"
    echo
}

if [ "$#" -ne 2 ]; then
    print_usage
    exit 1
fi

export INFISICAL_ENV=${1}

function provision_infrastructure {
    # TODO: need to create workspace if it doesn't exist
    ansible-playbook provision-infrastructure.yml -e operation=create -e terraform_workspace=${1}
}

function setup_infrastructure {
    ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i host.ini setup-backend.yml \
        -u ${TF_VAR_vm_user} --key-file '${TF_VAR_key_file}' -e terraform_workspace=${1} \
        -e @vars/${1}.yml
}

case $1 in
    "destroy")
        echo "Destroying \"$2\""
        ansible-playbook provision-infrastructure.yml -e operation=destroy -e terraform_workspace=${2}
        ;;

    "create")
        echo "Creating \"$2\""

        # provision
        provision_infrastructure "${2}"

        # setup
        setup_infrastructure "${2}"
        ;;

    "provision")
        echo "Provisioning \"$2\""
        provision_infrastructure "${2}"
        ;;

    "setup")
        echo "Setting up \"$2\""
        setup_infrastructure "${2}"
        ;;

    *)
        print_usage
        exit 1
esac
