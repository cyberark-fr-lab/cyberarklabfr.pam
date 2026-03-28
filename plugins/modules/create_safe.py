#!/usr/bin/python

# Copyright: (c) 2023, Jerome Coste <contact@jeromecoste.fr>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cyberarkfrlab.pam.plugins.module_utils.safe import (search_safes, verify_safe_name)

from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.six.moves.http_client import HTTPException

from ansible.module_utils.urls import open_url

import json

__metaclass__ = type

DOCUMENTATION = r'''
---
module: create_safe

short_description: Create a safe.

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: 
 - Create a safe.
   Changes if safe is created.
   Ok if safe is already exists.
   Fails if safe cannot be created or if there is an error.
   
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
              logged-on CyberArk session, please see M(cyberarkfrlab.pam.login) role for an example of cyberark_session.
        required: true
        type: dict
    name:
        description: Name of the safe
        required: true
        type: str
    cpm:
        description: Safe's managing cpm
        required: false
        default: ""
        type: str
    description:
        description: Safe's description
        required: false
        default: ""
        type: str
    location:
        description: Location of the safe in the Vault
        required: false
        default: \\
        type: str
    retention_days:
        description: The number of days that password versions are saved in the Safe.
        required: when C(retention_days) is not set
        type: int
    retention_versions:
        description: The number of retained versions of every password that is stored in the Safe.
        required: when C(retention_versions) is not set
        type: int
    auto_purge:
        description: 
            - Whether or not to automatically purge files after the end of the Object History 
              Retention Period defined in the Safe properties.
        required: false
        default: false
        type: bool
    olac:
        description: Is Object Level Access Control enabled.
        required: false
        default: false
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

- name: "Create safe"
  cyberarkfrlab.pam.create_safe:
    name: "My safe"
    cpm: "CPM-1234"
    retention_versions: 5
    cyberark_session: "{{ cyberark_session }}"

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
    description: Whether the module successfully created the safe.
    returned: always
    type: bool
response:
    description: Response from PAM containing the error
    returned: when not C(success)
    type: text
safes:
    description: List of safes found
    returned: when C(state)==present and C(multiple) and C(success)
    type: array of safe
safe:
    description: Safe found
    returned: when C(state)==present and when success
    type: complex
    contains:
        id:
            description: Safe's unique ID. (Also called SafeUrlId)
            returned: always
            type: str
            sample: "Linux_Accounts"
        description:
            description: Safe's description
            returned: always
            type: str
            sample: "Company's linux accounts, keys and passwords."
        name:
            description: Safe's name.
            returned: always
            type: str
            sample: "Linux_Accounts"
        number:
            description: Safe's unique number.
            returned: always
            type: int
            sample: 123
        cpm:
            description: Safe's managing cpm.
            returned: always
            type: str
            sample: "Password_Manager"
        olac:
            description: Is Object Level Access Control enabled.
            returned: always
            type: str
            sample: false
        created_time:
            description: Creation date (Unix Time).
            returned: always
            type: int
            sample: "1567824520"
        modified_time:
            description: Latest modification date (Unix Time).
            returned: always
            type: int
            sample: "1567824520"
        retention_days:
            description: The number of days that password versions are saved in the Safe.
            returned: when C(retention_days) is not configured
            type: int
            sample: 5
        retention_versions:
            description: The number of retained versions of every password that is stored in the Safe.
            returned: when C(retention_versions) is not configured
            type: int
            sample: 5
        location:
            description: The location of the safe in the Vault
            returned: always
            type: str
            sample: '\\'
        auto_purge:
            description: 
                - Whether or not to automatically purge files after the end of the Object History 
                  Retention Period defined in the Safe properties.
            returned: always
            type: bool
            sample: false
        creator:
            description: Information about the creator of the safe
            returned: always
            type: complex
            contains:
                id:
                    description: User ID.
                    returned: always
                    type: str
                    sample: "1"
                name:
                    description: Username of the creator.
                    returned: always
                    type: str
                    sample: "john.doe@company.tld"
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
        "name": {
            "required": True,
            "type": "str"
        },
        "cpm": {
            "type": "str",
            "default": "",
        },
        "description": {
            "type": "str",
            "default": "",
        },
        "location": {
            "type": "str",
            "default": '\\',
        },
        "retention_days": {
            "required": False,
            "type": "int"
        },
        "retention_versions": {
            "required": False,
            "type": "str"
        },
        "auto_purge": {
            "type": "bool",
            "default": False,
        },
        "olac": {
            "type": "bool",
            "default": False,
        }
    }

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False,
    )

    if not verify_safe_name(module.params['name']):
        module.fail_json(success=False, msg="Invalid safe name", response=module.params['name'])

    # # Search for safes with matching fields
    # search = search_safes(module)
    # if not search['success']:
    #     module.fail_json(success=False, msg="Search failed", response=search["content"])
    #
    # safes = search['content']
    # if len(safes) != 0:
    #     for safe in safes:
    #         if safe['id'] == module.params['name']:
    #             result = dict(changed=False, success=True, safe=safe)
    #             module.exit_json(**result)

    created = create_safe(module)
    if not created['success']:
        module.fail_json(success=False, msg="Safe creation failed", response=created["content"])

    # No safe with the same exact name
    result = dict(changed=created['changed'], success=True, safe=created['content'])
    module.exit_json(**result)


def create_safe(module):
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
    endpoint = "/PasswordVault/api/Safes"

    data = {
        'safeName': module.params["name"],
        'description': module.params["description"],
        'location': module.params["location"],
        'olacEnabled': module.params["olac"],
        'managingCPM': module.params["cpm"],
        'AutoPurgeEnabled': module.params["auto_purge"],
    }

    if 'retention_versions' in module.params:
        data['numberOfVersionsRetention'] = module.params['retention_versions']

    if 'retention_days' in module.params:
        data['numberOfDaysRetention'] = module.params['retention_days']

    try:
        response = open_url(
            api_base_url + endpoint,
            method="POST",
            headers=headers,
            validate_certs=validate_certs,
            data=json.dumps(data),
        )
    except(HTTPError, HTTPException) as http_exception:
        # 409 Conflict - Safe already exists
        if http_exception.getcode() == 409:
            return dict(changed=False, success=True, code=http_exception.getcode(), content=http_exception.read())

        # Other 40X errors or network exceptions
        return dict(changed=False, success=False, code=http_exception.getcode(), content=http_exception.read())

    # New safe created
    if response.getcode() == 201:
        return dict(changed=True, success=True, code=response.getcode(), content=response.read())

    # Default case. Other errors
    return dict(changed=False, success=False, code=response.getcode(), content=response.read())


def main():
    run_module()


if __name__ == '__main__':
    main()
