# cyberarkfrlab.pam.create_key

Generate an ssh key for a given username and onboard it to Cyberark PAM (Self Hosted or Privilege Cloud)

## Features
- [x] Create user (optionnal)
- [x] Generate ssh key (RSA 4096 bits)
- [x] Upload ssh key to CyberArk PAM

## Role variables

| Variable               | Required | Default                   | Choices | Comments                                                                     |
|------------------------|----------|---------------------------|---------|------------------------------------------------------------------------------|
| cyberark_session       | yes      | N/A                       |         | CyberArk session token and portal url. Obtained from cyberarkfrlab.pam.login |
| create_key_username    | yes      | N/A                       |         | User on ansible host (created if it doesn't exist)                           |
| create_key_address     | no       | Current host IPv4 address |         | IPv4 address of the host                                                     |
| create_key_safe_name   | yes      | N/A                       |         | Safe in which the key is stored                                              |
| create_key_platform_id | yes      | N/A                       |         | PAM platform associated to the account                                       |

## Example Playbook
```yaml
- hosts: all
  tasks:
    - name: "Login to PAM Web portal"
      ansible.builtin.include_role:
        name: cyberarkfrlab.pam.login
      vars:
        login_identity_url: "https://abc1234.id.cyberark.cloud"
        login_pam_url: "https://mycompany.privilegecloud.cyberark.cloud"
        login_pam_user: "pam-auto-onboarding@cyberark.cloud.1234"
        login_pam_pass: "A strong password"

    - name: "Create and upload ssh key"
      ansible.builtin.include_role:
        name: cyberarkfrlab.pam.create_key
      vars:
        create_key_username_username: "root"
        create_key_username_address: "0.0.0.0"
        create_key_username_safe_name: "Linux_Keys"
        create_key_username_platform_id: "UnixSSHKeys"

    - name: "Logout from Web portal"
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
TEST_PAM_USER: 'dpa-ansible-automation@cyberark.cloud.1234'
TEST_PAM_PASS: 'A strong password'
TEST_PAM_KEY_PLATFORM: 'UnixSSHKeys'
TEST_PAM_SAFE: 'Test_Linux_Keys'
```

**NB:** Alternatively, TEST_* variables can be defined as environment variables.

Then, run the test command:
```bash
$ molecule test -s create_key
$ echo $? # Should return 0
```

## License

GPLv3

## Author Information

Jérôme Coste   
contact@jeromecoste.fr | jerome.coste@cyberark.com
