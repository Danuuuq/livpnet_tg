from flask import Flask, request, jsonify, abort
import subprocess
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY", "CHANGEME")
CERT_OUTPUT_DIR = os.getenv("CERT_OUTPUT_DIR", "/etc/openvpn/clients/")  # Общая папка с nginx
SCRIPT_ADD = os.getenv("SCRIPT_ADD", "./add_client.sh")
SCRIPT_REVOKE = os.getenv("SCRIPT_REVOKE", "./revoke_client.sh")
PUBLIC_DOWNLOAD_URL = os.getenv("PUBLIC_DOWNLOAD_URL", "https://vpn.example.com/downloads")

app = Flask(__name__)


def check_auth():
    key = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    if key != API_KEY:
        abort(401, description="Unauthorized")


@app.route("/certificates/<name>", methods=["POST"])
def create_cert(name):
    check_auth()

    result = subprocess.run(
        ["/bin/bash", SCRIPT_ADD, name],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        return jsonify({"error": result.stderr.strip()}), 500

    lines = result.stdout.strip().splitlines()
    ovpn_path = lines[-1].strip() if lines else ""

    if not os.path.exists(ovpn_path):
        return jsonify({"error": "Сертификат не создан"}), 500

    # Вернуть публичную ссылку
    public_url = f"{PUBLIC_DOWNLOAD_URL}/{name}.ovpn"
    return jsonify({"message": "Сертификат создан", "download_url": public_url})


@app.route("/certificates/<name>", methods=["DELETE"])
def revoke_cert(name):
    check_auth()

    result = subprocess.run(
        ["/bin/bash", SCRIPT_REVOKE, name],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        return jsonify({"error": result.stderr.strip()}), 500

    return jsonify({"message": result.stdout.strip()})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})