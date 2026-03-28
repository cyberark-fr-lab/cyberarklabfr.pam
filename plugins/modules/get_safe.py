#!/usr/bin/python

# Copyright: (c) 2023, Jerome Coste <contact@jeromecoste.fr>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cyberarkfrlab.pam.plugins.module_utils.safe import search_safes

__metaclass__ = type

DOCUMENTATION = r'''
---
module: get_safe

short_description: Get safe's information.

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: 
 - Search for a safe based on its name.
   Succeed if exactly one safe is found
   Fails if no safe is found or if there is an error.

options:
    state:
        description:
            - Set to C(present) to verify safe exists.
              Set to C(absent) to verify safe doesn't exist.
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
              logged-on CyberArk session, please see M(cyberarkfrlab.pam.login) role for an example of cyberark_session.
        required: true
        type: dict
    name:
        description: Name of the safe
        required: true
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
  cyberarkfrlab.pam.get_safe:
    name: "Linux_Accounts"
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
    description: Whether the module successfully get safe(s).
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
            "required": False,
            "type": "str"
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

    # Search for safes with matching fields
    search = search_safes(module)
    if not search['success']:
        module.fail_json(success=False, msg="Search failed", response=search['content'])

    safes = search['content']
    # Handle case: Safe mustn't exist (state=absent)
    if module.params['state'] == 'absent':
        if len(safes) != 0:
            module.fail_json(success=False, msg='Found safe(s)')
        else:
            result = dict(changed=False, success=True)
            module.exit_json(**result)

    # Handle case: One safe must exist (state=present)
    if len(safes) == 0:
        module.fail_json(success=False, msg='No safe found', response=search['content'])

    if module.params['multiple']:
        result = dict(changed=False, success=True, safes=safes)
        module.exit_json(**result)

    # We must have exactly one safe
    if len(safes) > 1:
        module.fail_json(success=False, msg='Found multiple safes', response=search['content'])

    # Return safe
    result = dict(changed=False, success=True, safe=safes[0])
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
