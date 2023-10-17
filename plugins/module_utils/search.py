# Copyright: (c) 2023, Jerome Coste <contact@jeromecoste.fr>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.urls import open_url
from ansible.module_utils.six.moves.urllib.parse import quote

from ansible_collections.cyberarkfrlab.pam.plugins.module_utils.generic import rename_keys, filter_objects_by
from ansible_collections.cyberarkfrlab.pam.plugins.module_utils.request import req_get_build_url


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
def req_search_build_filter_param(mod_parameters):
    if "safe" in mod_parameters and mod_parameters["safe"] is not None:
        return "filter=" + quote("safeName eq ") + quote(mod_parameters["safe"])
    else:
        return ''


def search_accounts(module):
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
    url = req_get_build_url(api_base_url + endpoint,
                            [req_build_search_param(module.params), req_search_build_filter_param(module.params)])
    response = open_url(
        url,
        method="GET",
        headers=headers,
        validate_certs=validate_certs,
    )

    # Successful response
    if response.getcode() != 200:
        return dict(success=False, response=response, accounts=None)

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
        accounts = filter_objects_by(accounts, 'secret_type', module.params["secret_type"])

    return dict(success=True, response=response, accounts=accounts)
