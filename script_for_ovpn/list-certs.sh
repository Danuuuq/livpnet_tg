#!/bin/bash

# WARNING!!!!
# Made by ChatGPT
# Скрипт для просмотра статуса всех сертификатов

INDEX_FILE="/etc/openvpn/server/easy-rsa/pki/index.txt"

if [ ! -f "$INDEX_FILE" ]; then
    echo "index.txt not found!" >&2
    exit 1
fi

echo "["

first_entry=true
while IFS= read -r line; do
    [[ "$line" =~ CN=([^[:space:]]+) ]] || continue
    name="${BASH_REMATCH[1]}"

    if [[ "$line" =~ ^V ]]; then
        status="active"
    elif [[ "$line" =~ ^R ]]; then
        status="revoked"
    else
        status="unknown"
    fi

    if [ "$first_entry" = true ]; then
        first_entry=false
    else
        echo ","
    fi

    echo -n "  { \"name\": \"${name}\", \"status\": \"${status}\" }"
done < "$INDEX_FILE"

echo
echo "]"
