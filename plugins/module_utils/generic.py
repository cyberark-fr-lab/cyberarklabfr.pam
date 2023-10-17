# Copyright: (c) 2023, Jerome Coste <contact@jeromecoste.fr>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

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


# Return objects with object[key] == value
def filter_objects_by(objects, key, value):
    out_objects = []
    for account in objects:
        if value == account[key]:
            out_objects.append(account)

    return out_objects
