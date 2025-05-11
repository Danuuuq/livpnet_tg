#!/bin/bash

# WARNING!!!!
# Made by ChatGPT

set -e
CLIENT_NAME="$1"

cd /etc/openvpn/server/easy-rsa/
./easyrsa --batch revoke "$CLIENT_NAME"
./easyrsa gen-crl

rm -f "pki/private/${CLIENT_NAME}.key" "pki/reqs/${CLIENT_NAME}.req"
cp pki/crl.pem /etc/openvpn/server/crl.pem
chown nobody:nogroup /etc/openvpn/server/crl.pem
echo "Revoked $CLIENT_NAME"
