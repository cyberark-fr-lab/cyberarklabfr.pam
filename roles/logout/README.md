# cyberarkfrlab.pam.logout

Logout from Cyberark PAM (Self-Hosted)

## Features
- [x] Logout from CyberArk PAM Self Hosted or Privilege Cloud Standalone. Doesn't work with Privilege Cloud ISP.

## Role variables

| Variable         | Required | Default | Choices | Comments                                                                     |
|------------------|----------|---------|---------|------------------------------------------------------------------------------|
| cyberark_session | yes      | N/A     |         | CyberArk session token and portal url. Obtained from cyberarkfrlab.pam.login |

## Example Playbook
```yaml
- hosts: all
  tasks:
    - name: "Logout from PAM Web portal"
      ansible.builtin.include_role:
        name: cyberarkfrlab.pam.logout
```

## Run tests

### Prerequisites

Official molecule [installation instructions](https://ansible.readthedocs.io/projects/molecule/installation/)

### Configure and run

A Cyberark PAM environment and service account are required to test this role. \
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
$ molecule test -s logout
$ echo $? # Should return 0
```

## License

GPLv3

## Author Information

Jérôme Coste   
contact@jeromecoste.fr | jerome.coste@cyberark.com
