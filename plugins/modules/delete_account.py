#!/usr/bin/python

# Copyright: (c) 2023, Jerome Coste <contact@jeromecoste.fr>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import open_url

from ansible_collections.cyberarkfrlab.pam.plugins.module_utils.search import search_accounts

__metaclass__ = type

DOCUMENTATION = r'''
---
module: delete_account

short_description: Search and delete an account.

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: 
 - Search and delete an account based on fields such as name, username, address, safe and platform.
   Succeed if exactly one account is found, fails otherwise.

options:
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
    multiple:
        description: Delete all accounts matching identified_by fields
        required: false 
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

- name: "Delete operator account information"
  cyberarkfrlab.pam.delete_account:
    identified_by: "address,username,platform_id"
    username: "operator"
    address: "0.0.0.0"
    secret_type: "password"
    safe: "Linux_Passwords"
    platform_id: "UnixSSH"
  retries: 5
  delay: 10

- name: "Logout from PAM Web portal"
  ansible.builtin.include_role:
    name: cyberarkfrlab.pam.logout
'''

RETURN = r'''
changed:
    description: Identify if the module run resulted in a change to the account in any way.
    returned: always
    type: bool
failed:
    description: Whether the module run resulted in a failure of any kind.
    returned: always
    type: bool
success:
    description: Whether the module successfully deleted the account(s).
    returned: always
    type: bool
response:
    description: Response from PAM containing the error
    returned: when not success
    type: text
accounts:
    description: List of deleted accounts
    returned: when success
    type: json
'''


def run_module():
    module_args = {
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

    search = search_accounts(module)
    if not search['success']:
        result = dict(success=False, response=search['response'])
        module.fail_json(changed=False, **result)

    accounts = search['accounts']
    if len(accounts) == 0:
        result = dict(changed=False, success=True, accounts=accounts)
        module.exit_json(**result)

    accounts_to_delete = []
    if module.params["multiple"]:
        accounts_to_delete = accounts
    elif len(accounts) == 1:
        accounts_to_delete.append(accounts[0])
    else:
        deleted = dict(success=False, response=search['response'])
        module.fail_json(msg='Multiple accounts found', **deleted)

    # Start deletion
    for account_to_delete in accounts_to_delete:
        cyberark_session = module.params["cyberark_session"]
        if account_to_delete['secret_type'] == 'key':
            deleted = delete_key_account(cyberark_session, account_to_delete['id'])
            if not deleted['success']:
                result = dict(success=False, response=deleted['response'])
                module.fail_json(msg='Fail to delete key', **result)
        elif account_to_delete['secret_type'] == 'password':
            deleted = delete_password_account(cyberark_session, account_to_delete['id'])
            if not deleted['success']:
                result = dict(success=False, response=deleted['response'])
                module.fail_json(msg='Fail to delete password', **result)
        else:
            result = dict(success=False, response=account_to_delete)
            module.fail_json(msg='Account type not managed', **result)

    result = dict(changed=True, success=True, accounts=accounts_to_delete)
    module.exit_json(**result)


def delete_password_account(cyberark_session, account_id):
    # Craft URL
    url = f"{cyberark_session['api_base_url']}/PasswordVault/api/Accounts/{account_id}"

    # Delete account
    response = open_url(
        url,
        method="DELETE",
        headers={
            "Authorization": cyberark_session["token"],
            "User-Agent": "CyberArk/1.0 (Ansible; cyberarkfrlab.pam)"
        },
        validate_certs=cyberark_session["validate_certs"],
    )

    # Successful response
    if response.getcode() != 204:
        return dict(success=False, response=response)

    return dict(success=True, response=response)


def delete_key_account(cyberark_session, account_id):
    # Craft URL
    url = f"{cyberark_session['api_base_url']}/PasswordVault/WebServices/PIMServices.svc/Accounts/{account_id}"

    # Get all accounts that match safe, platform, user and address
    response = open_url(
        url,
        method="DELETE",
        headers={
            "Authorization": cyberark_session["token"],
            "User-Agent": "CyberArk/1.0 (Ansible; cyberarkfrlab.pam)"
        },
        validate_certs=cyberark_session["validate_certs"],
    )

    # Successful response
    if response.getcode() != 200:
        return dict(success=False, response=response)

    return dict(success=True, response=response)


def main():
    run_module()


if __name__ == '__main__':
    main()
