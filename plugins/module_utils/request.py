# Copyright: (c) 2023, Jerome Coste <contact@jeromecoste.fr>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Concatenate url with GET parameters.
# Eg: https://pvwa.tld/PasswordVault/api/Accounts?search=root%201.2.3.4%20sshkeys&filter=safeName%20eq%20SSH_Keys
def req_get_build_url(url, params):
    out_url = url
    prefix_token = '?'
    for req_param in params:
        out_url += prefix_token + req_param
        prefix_token = '&'

    return out_url
