# cyberarkfrlab.pam.delete_key

Delete an account with an ssh key from Cyberark PAM (Self Hosted or Privilege Cloud)

## Features
- [x] Delete account's ssh key from CyberArk PAM

## Role variables

| Variable               | Required | Default                          | Choices | Comments                                                                     |
|------------------------|----------|----------------------------------|---------|------------------------------------------------------------------------------|
| cyberark_session       | yes      | N/A                              |         | CyberArk session token and portal url. Obtained from cyberarkfrlab.pam.login |
| delete_key_username    | yes      | N/A                              |         | User on ansible host                                                         |
| delete_key_address     | no       | Current host IPv4 address        |         | IPv4 address of the host                                                     |
| delete_key_safe_name   | yes      | N/A                              |         | Safe in which the key is stored                                              |
| delete_key_platform_id | yes      | N/A                              |         | PAM platform associated to the account                                       |

## Example Playbook
```yaml
- hosts: all
  tasks:
    - name: "Login to CyberArk Web portal"
      ansible.builtin.include_role:
        name: cyberarkfrlab.pam.login
      vars:
        login_identity_url: "https://abc1234.id.cyberark.cloud"
        login_pam_url: "https://mycompany.privilegecloud.cyberark.cloud"
        login_pam_user: "pam-auto-onboarding@cyberark.cloud.1234"
        login_pam_pass: "A strong password"

    - name: "Delete root's ssh key from PAM"
      ansible.builtin.include_role:
        name: cyberarkfrlab.pam.delete_key
      vars:
        delete_key_user: "root"
        delete_key_address: "0.0.0.0"
        delete_key_safe_name: "Linux_Keys"
        delete_key_platform_id: "UnixSSHKeys"

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
TEST_PAM_USER: 'pam-auto-onboarding@cyberark.cloud.1234'
TEST_PAM_KEY_PLATFORM: 'UnixSSHKeys'
TEST_PAM_SAFE: 'Test_Linux_Keys'
```

**NB:** Alternatively, TEST_* variables can be defined as environment variables.

Then, run the test command:
```bash
$ molecule test -s delete_key
$ echo $? # Should return 0
```

## License

GPLv3

## Author Information

Jérôme Coste   
contact@jeromecoste.fr | jerome.coste@cyberark.com
