# Copyright: (c) 2023, Jerome Coste <contact@jeromecoste.fr>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.urls import open_url
from ansible.module_utils.six.moves.urllib.parse import quote

from ansible_collections.cyberarkfrlab.pam.plugins.module_utils.generic import rename_keys, filter_objects_by
from ansible_collections.cyberarkfrlab.pam.plugins.module_utils.request import req_get_build_url

from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.six.moves.http_client import HTTPException

import re


# Build search parameter for GET /Accounts
# Eg: search=root%201.2.3.4%20sshkeys
def req_safe_build_search_param(mod_parameters):
    if "name" not in mod_parameters or mod_parameters["name"] is None:
        return ''

    return "search" + "=" + quote(mod_parameters["name"])


# Search and return safes. Support search parameters
def search_safes(module):
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

    # Get all accounts that match safe, platform, user and address
    url = req_get_build_url(api_base_url + endpoint, [req_safe_build_search_param(module.params)])

    try:
        response = open_url(
            url,
            method="GET",
            headers=headers,
            validate_certs=validate_certs,
        )
    except(HTTPError, HTTPException) as http_exception:
        return dict(success=False, code=http_exception.getcode(), content=http_exception.read())

    # Successful response
    if response.getcode() != 200:
        return dict(success=False, code=response.getcode(), content=response.read())

    resp_data = json.loads(response.read())
    safes = resp_data["value"] if 'value' in resp_data else []

    # Filter found accounts by secret_type
    # The API search mechanism doesn't support filtering by secret_type, this has to be done here.
    safe_key_map = {
        'safeUrlId': 'id',
        'safeNumber': 'number',
        'safeName': 'name',
        'managingCPM': 'cpm',
        'creationTime': 'created_time',
        'lastModificationTime': 'modified_time',
        'numberOfDaysRetention': 'retention_days',
        'numberOfVersionsRetention': 'retention_versions',
        'autoPurgeEnabled': 'auto_purge',
        'olacEnabled': 'olac',
    }
    safes = rename_keys(safe_key_map, safes)

    return dict(success=True, content=safes)


def verify_safe_name(name):
    regex = re.compile('[/:*<>.|?"‰&+\\\\]')

    return regex.search(name) is None
