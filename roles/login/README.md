# cyberarkfrlab.pam.login

Login to Cyberark PAM (Self-Hosted or Privilege Cloud)

## Features
- [x] Authenticate to Privilege Access Manager Self-Hosted (as a CyberArk user, LDAP or other not supported)
- [x] Authenticate to Identity Security Platform (as a service account)

## Role variables

| Variable           | Required                 | Default | Choices | Comments                                                                 |
|--------------------|--------------------------|---------|---------|--------------------------------------------------------------------------|
| login_username     | yes                      | N/A     |         | Username to log into PAM Self-Hosted or Privilege Cloud                  |
| login_password     | yes                      | N/A     |         | Username's password                                                      |
| login_pam_url      | yes                      | N/A     |         | `https://pam.example.com` or `https://<subdomain>.privilegecloud.com`    |
| login_identity_url | if Privilege Cloud (ISP) | N/A     |         | `https://abc1234.my.idaptive.app` or `https://abc1234.id.cyberark.cloud` |

To create a PAM service user for Privilege Cloud (ISP):
1. Login to Identity Administration page
2. Go to Core Services > Users , then click Add User and complete the following fields
   - Login name
   - Display name
   - Password
3. In the Status checklist, select the Is OAuth confidential client checkbox
4. Click Create User
5. Assign the newly created service user to the Privilege Cloud Users role.
6. Assign the newly created service user to safes with the following permissions:
   - List accounts
   - Get account password
   - Create account
   - Modify account properties
   - Modify account password
   - Delete account

## Example Playbook
```yaml
- hosts: all
  tasks:
    - name: "Login to PAM Web portal"
      ansible.builtin.include_role:
        name: cyberarkfrlab.pam.login
      vars:
        identity_url: "https://abc1234.id.cyberark.cloud"
        pam_url: "https://mycompany.privilegecloud.cyberark.cloud"
        pam_user: "pam-auto-onboarding@cyberark.cloud.1234"
        pam_pass: "A strong password"
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
```

**NB:** Alternatively, TEST_* variables can be defined as environment variables.

Then, run the test command:
```bash
$ molecule test -s login
$ echo $? # Should return 0
```

## License

GPLv3

## Author Information

Jérôme Coste   
contact@jeromecoste.fr | jerome.coste@cyberark.com
