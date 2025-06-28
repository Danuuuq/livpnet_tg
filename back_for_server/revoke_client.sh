#!/bin/bash

set -e

CLIENT_NAME="$1"
EASYRSA_DIR="/etc/openvpn/server/easy-rsa"
CRL_PATH="/etc/openvpn/server/crl.pem"
OUTPUT_DIR="/etc/openvpn/clients"

cd "$EASYRSA_DIR" || exit 1

# Проверка: существует ли сертификат
if [[ ! -f "pki/issued/${CLIENT_NAME}.crt" ]]; then
  echo "Сертификат ${CLIENT_NAME} не найден." >&2
  exit 1
fi

# Отзыв сертификата
./easyrsa --batch revoke "$CLIENT_NAME"
./easyrsa gen-crl

# Очистка: удаление ключей и запроса
rm -f "pki/private/${CLIENT_NAME}.key" \
      "pki/reqs/${CLIENT_NAME}.req" \
      "pki/issued/${CLIENT_NAME}.crt"

# Удаление .ovpn, если есть
rm -f "$OUTPUT_DIR/${CLIENT_NAME}.ovpn"

# Обновление crl.pem
cp pki/crl.pem "$CRL_PATH"
chown nobody:nogroup "$CRL_PATH"

echo "Сертификат ${CLIENT_NAME} отозван и удалён."