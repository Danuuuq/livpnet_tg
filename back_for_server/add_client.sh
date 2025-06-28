#!/bin/bash

set -e

CLIENT_NAME="$1"

# Папка, куда сохраняется итоговый .ovpn
OUTPUT_DIR="/etc/openvpn/clients"
/usr/bin/mkdir -p "$OUTPUT_DIR"

# Перейти в Easy-RSA
cd /etc/openvpn/server/easy-rsa/ || exit 1

# Построить клиентский сертификат без пароля
./easyrsa --batch build-client-full "$CLIENT_NAME" nopass

# Путь к итоговому .ovpn
CONFIG_PATH="$OUTPUT_DIR/${CLIENT_NAME}.ovpn"

# Сгенерировать .ovpn файл
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

# Вернуть путь к файлу для Flask
echo "$CONFIG_PATH"