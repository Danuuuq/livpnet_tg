#!/bin/bash

# OpenVPN install script (fixed version)
# Usage: ./openvpn-install-fixed.sh your.domain.com

set -e

if [[ "$EUID" -ne 0 ]]; then
    echo "This installer must be run as root."
    exit 1
fi

if [[ -z "$1" ]]; then
    echo "Usage: $0 your.domain.com"
    exit 1
fi

server_domain="$1"
protocol="udp"
port="1194"
group_name="nogroup"
vpn_subnet="10.8.0.0"
vpn_netmask="255.255.255.0"
interface=$(ip route | grep default | awk '{print $5}' | head -n1)

# Enable IP forwarding
echo 'net.ipv4.ip_forward=1' > /etc/sysctl.d/99-openvpn-forward.conf
sysctl -w net.ipv4.ip_forward=1

# Install dependencies
apt-get update
apt-get install -y openvpn iptables openssl ca-certificates wget curl

# Prepare Easy-RSA
mkdir -p /etc/openvpn/server/easy-rsa/
easy_rsa_url="https://github.com/OpenVPN/easy-rsa/releases/download/v3.2.2/EasyRSA-3.2.2.tgz"
{ wget -qO- "$easy_rsa_url" || curl -sL "$easy_rsa_url"; } | tar xz -C /etc/openvpn/server/easy-rsa/ --strip-components 1
cd /etc/openvpn/server/easy-rsa/
./easyrsa --batch init-pki
./easyrsa --batch build-ca nopass
./easyrsa --batch build-server-full server nopass
./easyrsa --batch gen-crl

cp pki/ca.crt pki/issued/server.crt pki/private/server.key pki/crl.pem /etc/openvpn/server/
chown nobody:$group_name /etc/openvpn/server/crl.pem
chmod o+x /etc/openvpn/server/

# Generate TLS key
openvpn --genkey secret /etc/openvpn/server/tc.key

# Generate DH parameters
echo '-----BEGIN DH PARAMETERS-----
MIIBCAKCAQEA//////////+t+FRYortKmq/cViAnPTzx2LnFg84tNpWp4TZBFGQz
+8yTnc4kmz75fS/jY2MMddj2gbICrsRhetPfHtXV/WVhJDP1H18GbtCFY2VVPe0a
87VXE15/V8k1mE8McODmi3fipona8+/och3xWKE2rec1MKzKT0g6eXq8CrGCsyT7
YdEIqUuyyOP7uWrat2DX9GgdT0Kj3jlN9K5W7edjcrsZCwenyO4KbXCeAvzhzffi
7MA0BM0oNC9hkXL+nOmFg/+OTxIy7vKBg8P+OxtMb61zO7X8vC7CIAXFjvGDfRaD
ssbzSibBsu/6iGtCOGEoXJf//////////wIBAg==
-----END DH PARAMETERS-----' > /etc/openvpn/server/dh.pem

# OpenVPN server config
cat > /etc/openvpn/server/server.conf <<EOF
port $port
proto $protocol
dev tun
ca ca.crt
cert server.crt
key server.key
dh dh.pem
auth SHA512
tls-crypt tc.key
topology subnet
server $vpn_subnet $vpn_netmask
ifconfig-pool-persist ipp.txt
push "redirect-gateway def1 bypass-dhcp"
push "dhcp-option DNS 8.8.8.8"
push "dhcp-option DNS 8.8.4.4"
push "block-outside-dns"
keepalive 10 120
user nobody
group $group_name
persist-key
persist-tun
verb 3
crl-verify crl.pem
explicit-exit-notify
EOF

# iptables rules
iptables -t nat -A POSTROUTING -s $vpn_subnet/24 -o "$interface" -j MASQUERADE
iptables -A FORWARD -s $vpn_subnet/24 -j ACCEPT
iptables -A FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A INPUT -p $protocol --dport $port -j ACCEPT

# Create client-common.txt
cat > /etc/openvpn/server/client-common.txt <<EOF
client
dev tun
proto $protocol
remote $server_domain $port
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
auth SHA512
ignore-unknown-option block-outside-dns
verb 3
EOF

# Enable and start OpenVPN
systemctl enable --now openvpn-server@server

echo "✅ OpenVPN installed and configured successfully."
echo "🌐 Server domain: $server_domain"
