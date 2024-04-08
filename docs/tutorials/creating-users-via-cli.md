# Creating users via the command line interface

Full command line interface (CLI) reference can be found [here](../reference/cli.md).

## Prerequisites

You will need to be able to SSH into the VM running the backend (TODO: move to a separate page).

Usually the person who deployed the VM will have SSH access to the VM. In order for other people to access the VM they will need to create
an SSH key pair and share the public key with the person who created the VM, who will then have to add that key to the *authorized_keys* file
on the VM.

An SSH keypair could be generated using

```
ssh-keygen
```

Check the options for that command so that you know what you are doing. You may already have one in your *~/.ssh* directory. The file ending in *.pub* is the public key that should be shared, the one with no extension
is private and should not be shared but will be used to connect to the VM.

## CLI basics

On the VM, you should be able to use the CLI with the command `tinymotion-backend`, for example you could print the version of the backend using:

```
tinymotion-backend version
```

Print the list of available commands using:

```
tinymotion-backend --help
```

This should show a number of commands, one of which will be `user`.

List the available sub-commands for the `user` command:

```
tinymotion-backend user --help
```

You should be able to see a number of `user` sub-commands, including `create`, `delete`, `update` and `list`.

You can run the sub-command with the `--help` option to view usage information for each of the sub-commands too, e.g.

```
tinymotion-backend user create --help
```

## List existing users

To list existing users run:

```
tinymotion-backend user list
```

This should give output in JSON format, which could look something like:

```json
[
  {
    "access_key": "mysecretaccesskey",
    "user_id": "bca7af43-6fc8-456b-b59b-389aeeae3dc4",
    "disabled": false,
    "email": "testuser1@example.com"
  },
  {
    "access_key": "anothersecretkey",
    "user_id": "3203a857-7f11-44b8-96b6-c319ea437d4e",
    "disabled": false,
    "email": "testuser2@example.com"
  }
]
```
if there were two users in the system.

## Create a new user

Let's create a new user with the command:

```
tinymotion-backend user create -e myuser@example.com -k myuseraccesskey
```

You can see from the output of `tinymotion-backend user create --help` that the `-e` option sets the email of the new user and `-k` the access key.

If successful, the above command will output the new user in JSON format, e.g.

```json
{
  "access_key": "myuseraccesskey",
  "user_id": "cbae11b5-1bd0-4686-8784-e1dafd952126",
  "disabled": false,
  "email": "myuser@example.com"
}
```

Note the `user_id` will be a randomly generated [UUID](https://en.wikipedia.org/wiki/Universally_unique_identifier) so will be different to the one above but will have the same format.

## List users again

Verify that your new user shows up now when you run:

```
tinymotion-backend user list
```

## Modifying a user's access key

Let's try changing the access key of the user we just created, using the `user update` command.

First run `tinymotion-backend user update --help` to see the available options.

Using the example new user above, we could run:

```
tinymotion-backend user update -k updatedaccesskey cbae11b5-1bd0-4686-8784-e1dafd952126
```

Note that we have to pass the `user_id` as an argument to the above function. You will need to use the correct `user_id` for the user that you just created.

If successful the above command should output the updated user record in JSON format, e.g.

```json
{
  "access_key": "updatedaccesskey",
  "user_id": "cbae11b5-1bd0-4686-8784-e1dafd952126",
  "disabled": false,
  "email": "myuser@example.com"
}
```
