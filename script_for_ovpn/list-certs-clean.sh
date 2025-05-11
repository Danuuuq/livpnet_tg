#!/bin/bash

# WARNING!!!!
# Made by ChatGPT
# Скрипт для просмотра статуса актуальных сертификатов

INDEX_FILE="/etc/openvpn/server/easy-rsa/pki/index.txt"
declare -A client_status

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

    # Перезаписываем: остаётся последняя строка для каждого имени
    client_status["$name"]="$status"
done < "$INDEX_FILE"

# Генерация JSON
echo "["
first=true
for name in "${!client_status[@]}"; do
    $first || echo ","
    first=false
    echo -n "  { \"name\": \"${name}\", \"status\": \"${client_status[$name]}\" }"
done
echo
echo "]"
