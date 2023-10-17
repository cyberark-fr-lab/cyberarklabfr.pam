#!/usr/bin/python

# Copyright: (c) 2023, Jerome Coste <contact@jeromecoste.fr>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cyberarkfrlab.pam.plugins.module_utils.search import search_accounts

__metaclass__ = type

DOCUMENTATION = r'''
---
module: get_account

short_description: Search and return an account (no the secret).

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: 
 - Search for an account based on fields such as name, username, address, safe and platform.
   Succeed if exactly one account is found, fails otherwise.
   Only basic account information (from GET /Accounts) is returned.

options:
    state:
        description:
            - Assert the desired state of the account C(present) to create or update and account object.
              Set to C(absent) for deletion of an account object.
        required: false
        default: present
        choices: [present, absent]
        type: str
    validate_certs:
        description:
            - If C(false), TLS certificate chain will not be validated.
              This should only set to C(true) if you have a root CA certificate installed on each node.
        required: false
        default: true
        type: bool
    cyberark_session:
        description:
            - Dictionary set by a CyberArk authentication containing the different values to perform actions on a 
              logged-on CyberArk session, please see M(cyberark.pas.cyberark_authentication) module for an
              example of cyberark_session.
        required: true
        type: dict
    safe:
        description: The safe in PAM where the privileged account is to be located.
        required: true
        type: str
    identified_by:
        description:
            - This parameter is used to confidently identify a single account when the default query can return
              multiple results.
        required: false
        default: username,address,platform_id
        type: str
    username:
        description: Account's username.
        required: false
        type: str
    address:
        description: Account's address.
        required: false
        type: str
    platform_id:
        description: Id of the platform associated with the account.
        required: false
        type: str
    name:
        description: ObjectID of the account. If used, identified_by fields are ignored.
        required: false
        type: str
    secret_type:
        description: Type of account's secret.
        required: false
        default: password
        choices: [password, key]
        type: str
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
# extends_documentation_fragment:
#     - my_namespace.my_collection.my_doc_fragment_name

author:
    - Jérôme Coste (@Kanabos)
'''

EXAMPLES = r'''
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

- name: "Logout from PAM Web portal"
  ansible.builtin.include_role:
    name: cyberarkfrlab.pam.logout
'''

RETURN = r'''
changed:
    description: Identify if the playbook run resulted in a change to the account in any way.
    returned: always
    type: bool
failed:
    description: Whether playbook run resulted in a failure of any kind.
    returned: always
    type: bool
success:
    description: Whether the module successfully get account(s).
    returned: always
    type: bool
response:
    description: Response from PAM containing the error
    returned: when not success
    type: text
accounts:
    description: List of accounts found
    returned: when state==present and multiple and success
    type: array of account
account:
    description: Account found
    returned: when state==present and when success
    type: complex
    contains:
        id:
            description: Internal ObjectID for the account
            returned: always
            type: int
            sample: "25_21"
        safe:
            description: The safe in PAM where the privileged account is to be located.
            returned: successful addition and modification
            type: str
            sample: Domain_Admins
        username:
            description: The username of the account
            returned: if C(username) is a property of the platform
            type: str
            sample: Administrator
        address:
            description: The address of the account
            returned: if C(address) is a property of the platform
            type: str
            sample: 1.2.3.4
        platform_id:
            description: The id of the platform associated with the account.
            returned: successful addition and modification
            type: str
            sample: WinServerLocal
        name:
            description: The external ObjectID of the account
            returned: successful addition and modification
            type: str
            sample:
                - Operating System-WinServerLocal-cyberark.local-administrator
        secret_type:
            description: Type of account's secret
            returned: successful addition and modification
            type: list
            sample:
                - key
                - password
        created_time:
            description: Timeframe calculation of the timestamp of account creation.
            returned: always
            type: int
            sample: "1567824520"
        platform_account_properties:
            description:
                - Object containing key-value pairs to associate with the
                  account, as defined by the account platform.
            returned: always
            type: complex
            contains:
                KEY VALUE:
                    description:
                        - Object containing key-value pairs to associate with the
                          account, as defined by the account platform.
                    returned: successful addition and modification
                    type: str
                    sample:
                        - "LogonDomain": "cyberark"
                        - "Port": "22"
        secret_management:
            description: Set of parameters associated with the management of the credential.
            returned: successful addition and modification
            type: complex
            contains:
                automaticManagementEnabled:
                    description:
                        - Parameter that indicates whether the CPM will manage
                          the password or not.
                    returned: successful addition and modification
                    type: bool
                lastModifiedTime:
                    description:
                        - Timeframe calculation of the timestamp of account
                          modification.
                    returned: successful addition and modification
                    type: int
                    sample: "1567824520"
                manualManagementReason:
                    description:
                        - Reason for disabling automatic management of the account
                    returned: if C(automaticManagementEnabled) is set to false
                    type: str
                    sample: This is a static account
'''


def run_module():
    module_args = {
        "state": {
           "type": "str",
           "choices": ["present", "absent"],
           "default": "present",
        },
        "validate_certs": {
            "type": "bool",
            "default": "true"
        },
        "cyberark_session": {
            "required": True,
            "type": "dict",
            "no_log": True
        },
        "safe": {
            "required": True,
            "type": "str"
        },
        "identified_by": {
            "type": "str",
            "default": "username,address,platform_id",
        },
        "username": {
            "required": False,
            "type": "str"
        },
        "address": {
            "required": False,
            "type": "str"
        },
        "platform_id": {
            "required": False,
            "type": "str"
        },
        "name": {
            "required": False,
            "type": "str"
        },
        "secret_type": {
            "required": False,
            "type": "str",
            "choices": ["password", "key"],
            "default": "password",
        },
        "multiple": {
            "type": "bool",
            "default": "false"
        },
    }

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # Search for accounts with matching fields
    search = search_accounts(module)
    if not search['success']:
        result = dict(success=False, response=search['response'])
        module.fail_json(msg="Search failed", **result)

    accounts = search['accounts']
    # Handle case: Account mustn't exist (state=absent)
    if module.params['state'] == 'absent':
        if len(accounts) != 0:
            result = dict(success=False, response=accounts)
            module.fail_json(msg='Found one account or more', **result)
        else:
            result = dict(changed=False, success=True)
            module.exit_json(**result)

    # Handle case: One account must exist (state=present)
    if len(accounts) == 0:
        result = dict(success=False, response=None)
        module.fail_json(msg='Found no account', **result)

    if module.params['multiple']:
        result = dict(changed=False, success=True, accounts=accounts)
        module.exit_json(**result)

    # We must have exactly one account
    if len(accounts) > 1:
        result = dict(success=False, response=accounts)
        module.fail_json(msg='Found one account or more', **result)

    # Return account
    result = dict(changed=False, success=True, account=accounts[0])
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
