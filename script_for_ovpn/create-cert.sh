#!/bin/bash

# WARNING!!!!
# Made by ChatGPT

set -e
CLIENT_NAME="$1"
cd /etc/openvpn/server/easy-rsa/
./easyrsa --batch build-client-full "$CLIENT_NAME" nopass

# Генерация .ovpn
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CONFIG_PATH="$SCRIPT_DIR/${CLIENT_NAME}.ovpn"

{
  cat /etc/openvpn/server/client-common.txt
  echo "<ca>"
  cat pki/ca.crt
  echo "</ca>"
  echo "<cert>"
  sed -ne '/BEGIN CERTIFICATE/,$ p' "pki/issued/${CLIENT_NAME}.crt"
  echo "</cert>"
  echo "<key>"
  cat "pki/private/${CLIENT_NAME}.key"
  echo "</key>"
  echo "<tls-crypt>"
  sed -ne '/BEGIN OpenVPN Static key/,$ p' /etc/openvpn/server/tc.key
  echo "</tls-crypt>"
} > "$CONFIG_PATH"

echo "$CONFIG_PATH"
