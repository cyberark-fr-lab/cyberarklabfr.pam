# Ansible Collection - cyberarkfrlab.pam

A collection of roles for Privilege Access Manager (Self-Hosted or Privilege Cloud):

| Role                              | Description                                       |
|-----------------------------------|---------------------------------------------------|
| cyberarkfrlab.pam.login           | Login to PAM (Self-Hosted or Privilege Cloud)     |
| cyberarkfrlab.pam.logout          | Logout from PAM (Self-Hosted or Privilege Cloud)  |
| cyberarkfrlab.pam.create_password | Create a password for a user and upload it to PAM |
| cyberarkfrlab.pam.delete_password | Delete the password of a user from PAM            |
| cyberarkfrlab.pam.create_key      | Create an ssh key for a user and upload it to PAM |
| cyberarkfrlab.pam.delete_key      | Delete the ssh key of a user from PAM             |

## Using this collection

### Installing the Collection from Ansible Galaxy

Before using this collection, you need to install it with the Ansible Galaxy command-line tool:
```bash
ansible-galaxy collection install cyberarkfrlab.pam
```

You can also include it in a `requirements.yml` file and install it with `ansible-galaxy collection install -r requirements.yml`, using the format:
```yaml
---
collections:
- name: cyberarkfrlab.pam
```

Note that if you install the collection from Ansible Galaxy, it will not be upgraded automatically when you upgrade the `ansible` package. To upgrade the collection to the latest available version, run the following command:
```bash
ansible-galaxy collection install cyberarkfrlab.pam --upgrade
```

You can also install a specific version of the collection, for example, if you need to downgrade when something is broken in the latest version (please report an issue in this repository). Use the following syntax to install version `0.1.0`:

```bash
ansible-galaxy collection install cyberarkfrlab.pam:==1.0.0
```

See [Ansible Using collections](https://docs.ansible.com/ansible/devel/user_guide/collections_using.html) for more details.

## Example Playbooks

### Example 1 - On each host, generate operator's password and upload it to PAM
```yaml
- hosts: all
  tasks:
    - name: "Login to PAM Web portal"
      ansible.builtin.include_role:
        name: cyberarkfrlab.pam.login
      vars:
        login_pam_user: "pam-auto-onboarding@cyberark.cloud.1234"
        login_pam_pass: "A strong password"
        login_pam_url: "https://company.privilegecloud.cyberark.cloud"
        login_identity_url: "https://abc1234.id.cyberark.cloud"

    - name: "Generate and upload password for user operator"
      ansible.builtin.include_role:
        name: cyberarkfrlab.pam.create_password
      vars:
        create_password_username: "operator"
        create_password_address: "0.0.0.0"
        create_password_safe_name: "Linux_Passwords"
        create_password_platform_id: "UnixSSH"

    - name: "Logout from PAM Web portal"
      ansible.builtin.include_role:
        name: cyberarkfrlab.pam.logout
```

### Example 2 - On each host, set operator's password and upload it to PAM
```yaml
- hosts: all
  tasks:
    - name: "Login to PAM Web portal"
      ansible.builtin.include_role:
        name: cyberarkfrlab.pam.login
      vars:
        login_pam_user: "pam-auto-onboarding@cyberark.cloud.1234"
        login_pam_pass: "A strong password"
        login_pam_url: "https://company.privilegecloud.cyberark.cloud"
        login_identity_url: "https://abc1234.id.cyberark.cloud"

    - name: "Set and upload specified password for user operator"
      ansible.builtin.include_role:
        name: cyberarkfrlab.pam.create_password
      vars:
        create_password_username: "operator"
        create_password_address: "0.0.0.0"
        create_password_password: "A strong password"
        create_password_safe_name: "Linux_Passwords"
        create_password_platform_id: "UnixSSH"

    - name: "Logout from PAM Web portal"
      ansible.builtin.include_role:
        name: cyberarkfrlab.pam.logout
```

### Example 3 - On each host, generate a key for user operator and upload it to PAM
```yaml
- hosts: all
  tasks:
    - name: "Login to PAM Web portal"
      ansible.builtin.include_role:
        name: cyberarkfrlab.pam.login
      vars:
        login_pam_user: "pam-auto-onboarding@cyberark.cloud.1234"
        login_pam_pass: "A strong password"
        login_pam_url: "https://company.privilegecloud.cyberark.cloud"
        login_identity_url: "https://abc1234.id.cyberark.cloud"

    - name: "Generate and upload SSH key for user operator"
      ansible.builtin.include_role:
        name: cyberarkfrlab.pam.create_key
      vars:
        create_key_username: "operator"
        create_key_address: "0.0.0.0"
        create_key_safe_name: "Linux_Keys"
        create_key_platform_id: "UnixSSHKeys"

    - name: "Logout from PAM Web portal"
      ansible.builtin.include_role:
        name: cyberarkfrlab.pam.logout
```

### Example 4 - Get Account information from Vault
```yaml
- hosts: all
  tasks:
    - name: "Login to PAM Web portal"
      ansible.builtin.include_role:
        name: cyberarkfrlab.pam.login
      vars:
        login_pam_user: "pam-auto-onboarding@cyberark.cloud.1234"
        login_pam_pass: "A strong password"
        login_pam_url: "https://company.privilegecloud.cyberark.cloud"
        login_identity_url: "https://abc1234.id.cyberark.cloud"

    - name: "Get operator account information"
      cyberarkfrlab.pam.get_account:
        identified_by: "address,username,platform_id"
        username: "operator"
        address: "0.0.0.0"
        secret_type: "password"
        safe: "Linux_Passwords"
        platform_id: "UnixSSH"
        state: "present"
      retries: 5
      delay: 10
      loop: "{{ accounts }}"
      loop_control:
        loop_var: "account"

    - name: "Logout from PAM Web portal"
      ansible.builtin.include_role:
        name: cyberarkfrlab.pam.logout
```

## TODO
 - [ ] Delete password or key from target