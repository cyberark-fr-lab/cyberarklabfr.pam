#!/usr/bin/env bash

## Logging functions

C_TEST="\033[38;5;226m"
C_PASS="\033[38;5;34m"
C_FAIL="\033[0;38;5;124m"

# log <COLOR> <TYPE> <CONTENT>
log () {
    local NO_FORMAT="\033[0m"
    local BOLD="\033[1m"
    echo -e "${BOLD}$1$2: [$3]${NO_FORMAT}"
}

# check_test <test> <test_return>
check_test () {
  if [ $2 -eq 0 ]; then
    log "$C_PASS" "pass" "$1"
  else
    log "$C_FAIL" "fail" "$1"
    exit 1
  fi
}

# Run all role tests
mol_tests=("login" "logout" "create_safe" "delete_safe" "get_safe" "get_account" "delete_account" "create_password" "delete_password" "create_key" "delete_key")
for mol_test in "${mol_tests[@]}"; do
  log "$C_TEST" "test" "$mol_test"
  molecule -v test -s "$mol_test"
  check_test "$mol_test" $?
  echo ""
done