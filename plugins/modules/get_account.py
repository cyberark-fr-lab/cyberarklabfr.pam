#!/usr/bin/python

# Copyright: (c) 2023, Jerome Coste <contact@jeromecoste.fr>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import open_url
from ansible.module_utils.six.moves.urllib.parse import quote
import json

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
            - If C(false), SSL certificate chain will not be validated.
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
        description: The safe in the Vault where the privileged account is to be located.
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
  loop: "{{ accounts }}"
  loop_control:
    loop_var: "account"

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
result:
    description: A json dump of the resulting action.
    returned: success
    type: complex
    contains:
        id:
            description: Internal ObjectID for the account
            returned: always
            type: int
            sample: "25_21"
        safe:
            description: The safe in the Vault where the privileged account is to be located.
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
    }

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # List accounts #
    cyberark_session = module.params["cyberark_session"]

    # Authentication header
    headers = {
        "Content-Type": "application/json",
        "Authorization": cyberark_session["token"],
        "User-Agent": "CyberArk/1.0 (Ansible; cyberarkfrlab.pam)"
    }

    # Craft URL
    api_base_url = cyberark_session["api_base_url"]
    validate_certs = cyberark_session["validate_certs"]
    endpoint = "/PasswordVault/api/Accounts"

    # Get all accounts that match safe, platform, user and address
    url = req_build_url(api_base_url + endpoint, [req_build_search_param(module.params), req_build_filter_param(module.params)])
    response = open_url(
        url,
        method="GET",
        headers=headers,
        validate_certs=validate_certs,
    )

    # Successful response
    if response.getcode() != 200:
        result = {}
        module.fail_json(msg='Fail to list accounts!', **result)
    resp_data = json.loads(response.read())
    accounts = resp_data["value"] if 'value' in resp_data else []

    # Filter found accounts by secret_type
    # This filter cannot be used in the GET /Accounts call
    account_key_map = {
        'categoryModificationTime': 'modified_time',
        'createdTime': 'created_time',
        'secretType': 'secret_type',
        'platformAccountProperties': 'platform_account_properties',
        'platformId': 'platform_id',
        'safeName': 'safe',
        'secretManagement': 'secret_management',
        'userName': 'username'
    }
    accounts = rename_keys(account_key_map, accounts)
    if 'secret_type' in module.params and module.params["secret_type"] is not None:
        accounts = filter_accounts_by('secret_type', module.params["secret_type"], accounts)

    if module.params['state'] == 'absent':
        if len(accounts) != 0:
            result = {}
            module.fail_json(msg='Found at least one account', **result)
        else:
            result = dict(changed=False)
            module.exit_json(**result)

    # We assume state is 'present'
    if len(accounts) == 0:
        result = {}
        module.fail_json(msg='Found no account', **result)

    # We must have exactly one account
    if len(accounts) > 1:
        result = dict(json=accounts, changed=False)
        module.fail_json(msg='More than one account found', **result)

    # Return account
    result = dict(result=accounts[0], changed=False)
    module.exit_json(**result)


# Build search parameter for GET /Accounts
# Eg: search=root%201.2.3.4%20sshkeys
def req_build_search_param(mod_parameters):
    if "name" in mod_parameters and mod_parameters["name"] is not None:
        return "search" + "=" + quote(mod_parameters["name"])

    search_string = ''
    for account_field in mod_parameters["identified_by"].split(","):
        if account_field in mod_parameters and mod_parameters[account_field] is not None:
            search_string += (" " if search_string != '' else '') + mod_parameters[account_field]

    # Build the search request based on identified fields
    if len(search_string) > 0:
        search_string = "search=" + quote(search_string)

    return search_string


# Build filter parameter for GET /Accounts
# Eg: filter=safeName%20eq%20SSH_Keys
def req_build_filter_param(mod_parameters):
    if "safe" in mod_parameters and mod_parameters["safe"] is not None:
        return "filter=" + quote("safeName eq ") + quote(mod_parameters["safe"])
    else:
        return ''


def filter_accounts_by(key, value, accounts):
    out_accounts = []
    for account in accounts:
        if value == account[key]:
            out_accounts.append(account)

    return out_accounts


# Concatenate url with GET parameters.
# Eg: https://pvwa.tld/PasswordVault/api/Accounts?search=root%201.2.3.4%20sshkeys&filter=safeName%20eq%20SSH_Keys
def req_build_url(url, params):
    out_url = url
    prefix_token = '?'
    for req_param in params:
        out_url += prefix_token + req_param
        prefix_token = '&'

    return out_url


# Rename accounts' keys to key_map keys
def rename_keys(key_map, accounts):
    out_accounts = []
    for account in accounts:
        # Create a copy we can modify
        out_account = account.copy()
        for key in account:
            if key in key_map:
                out_account[key_map[key]] = out_account.pop(key)
        # Output modified account
        out_accounts.append(out_account)

    return out_accounts


def main():
    run_module()


if __name__ == '__main__':
    main()
