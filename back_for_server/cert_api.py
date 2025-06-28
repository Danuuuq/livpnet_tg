from flask import Flask, request, jsonify, abort
import subprocess
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY", "CHANGEME")
CERT_OUTPUT_DIR = os.getenv("CERT_OUTPUT_DIR", "/etc/openvpn/clients/")
SCRIPT_ADD = os.getenv("SCRIPT_ADD", "./add_client.sh")
SCRIPT_REVOKE = os.getenv("SCRIPT_REVOKE", "./revoke_client.sh")
PUBLIC_DOWNLOAD_URL = os.getenv("PUBLIC_DOWNLOAD_URL", "https://vpn.example.com/downloads")

app = Flask(__name__)


def check_auth():
    key = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    if key != API_KEY:
        abort(401, description="Unauthorized")


@app.route("/certificates", methods=["POST"])
def create_cert():
    check_auth()

    json_data = request.get_json()
    name = json_data.get("name")
    if not name:
        return jsonify({
            "success": False,
            "message": "Поле 'name' обязательно"
        }), 400

    result = subprocess.run(
        ["/bin/bash", SCRIPT_ADD, name],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        return jsonify({
            "success": False,
            "message": "Ошибка при создании сертификата",
            "details": result.stderr.strip(),
            "log": result.stdout.strip()
        }), 500

    lines = result.stdout.strip().splitlines()
    ovpn_path = lines[-1].strip() if lines else ""

    if not os.path.exists(ovpn_path):
        return jsonify({
            "success": False,
            "message": "Сертификат не был создан",
            "expected_path": ovpn_path,
            "log": result.stdout.strip()
        }), 500

    public_url = f"{PUBLIC_DOWNLOAD_URL}/{name}.ovpn"
    return jsonify({
        "success": True,
        "message": "Сертификат успешно создан",
        "download_url": public_url
    }), 201


@app.route("/certificates/<string:name>", methods=["DELETE"])
def revoke_cert(name: str):
    check_auth()

    if not name:
        return jsonify({
            "success": False,
            "message": "Поле 'name' обязательно"
        }), 400

    result = subprocess.run(
        ["/bin/bash", SCRIPT_REVOKE, name],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        return jsonify({
            "success": False,
            "message": "Ошибка при отзыве сертификата",
            "details": result.stderr.strip()
        }), 500

    return jsonify({
        "success": True,
        "message": f"Сертификат '{name}' отозван"
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})
