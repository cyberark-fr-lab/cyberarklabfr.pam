# cyberarkfrlab.pam.create_password

Set a password for a given username and onboard it to Cyberark PAM (Self Hosted or Privilege Cloud)

## Features
- [x] Create user (optionnal)
- [x] Generate a password (24 characters)
- [x] Upload password to CyberArk PAM

## Role variables

| Variable                    | Required | Default                          | Choices | Comments                                                                     |
|-----------------------------|----------|----------------------------------|---------|------------------------------------------------------------------------------|
| cyberark_session            | yes      | N/A                              |         | CyberArk session token and portal url. Obtained from cyberarkfrlab.pam.login |
| create_password_username    | yes      | N/A                              |         | User on ansible host (created if it doesn't exist)                           |
| create_password_address     | no       | Current host IPv4 address        |         | IPv4 address of the host                                                     |
| create_password_password    | no       | Randomly generated 24 characters |         | User's password                                                              |
| create_password_safe_name   | yes      | N/A                              |         | Safe in which the password is stored                                         |
| create_password_platform_id | yes      | N/A                              |         | PAM platform associated to the account                                       |

## Example Playbook
```yaml
- hosts: all
  tasks:
    - name: "Login to PAM Web portal"
      ansible.builtin.include_role:
        name: cyberarkfrlab.pam.login
      vars:
        login_identity_url: "abc1234.id.cyberark.cloud"
        login_pam_url: "mycompany.privilegecloud.cyberark.cloud"
        login_pam_user: "pam-auto-onboarding@cyberark.cloud.1234"
        login_pam_pass: "A strong password"

    - name: "Create and upload password for root"
      ansible.builtin.include_role:
        name: cyberarkfrlab.pam.create_password
      vars:
        create_password_username: "root"
        create_password_address: "0.0.0.0"
        create_password_password: "A strong password"
        create_password_safe_name: "Linux_Passwords"
        create_password_platform_id: "UnixSSH"

    - name: "Logout from PAM Web portal"
      ansible.builtin.include_role:
        name: cyberarkfrlab.pam.logout
```

## Run tests

### Prerequisites

Official molecule [installation instructions](https://ansible.readthedocs.io/projects/molecule/installation/)

### Configure and run

A Cyberark PAM environnement and service account are required to test this role. \
Create an `.env.yml` file as such:
```yaml
TEST_IDENTITY_URL: 'https://abc1234.id.cyberark.cloud'
TEST_PAM_URL: 'https://company.privilegecloud.cyberark.cloud'
TEST_PAM_USER: 'pam-auto-onboarding@cyberark.cloud.1234'
TEST_PAM_PASS: 'A strong password'
TEST_PAM_PWD_PLATFORM: 'UnixSSH'
TEST_PAM_SAFE: 'Test_Linux_Passwords'
```

**NB:** Alternatively, TEST_* variables can be defined as environment variables.

Then, run the test command:
```bash
$ molecule test -s create_password
$ echo $? # Should return 0
```

## License

GPLv3

## Author Information

Jérôme Coste   
contact@jeromecoste.fr | jerome.coste@cyberark.com
