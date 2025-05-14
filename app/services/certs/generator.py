import asyncio
from pathlib import Path


CERT_STORAGE = Path("storage/certs")


async def generate_certificate(cert_name: str) -> Path:
    CERT_STORAGE.mkdir(parents=True, exist_ok=True)

    # Строим команду
    cmd = [
        "docker", "exec", "openvpn_container",
        "easyrsa", "build-client-full", cert_name, "nopass"
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        raise RuntimeError(f"Ошибка генерации: {stderr.decode()}")

    # Получаем ovpn-файл
    ovpn_cmd = [
        "docker", "exec", "openvpn_container",
        "ovpn_getclient", cert_name
    ]
    ovpn_proc = await asyncio.create_subprocess_exec(
        *ovpn_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    ovpn_stdout, ovpn_stderr = await ovpn_proc.communicate()

    if ovpn_proc.returncode != 0:
        raise RuntimeError(f"Ошибка получения OVPN-файла: {ovpn_stderr.decode()}")

    file_path = CERT_STORAGE / f"{cert_name}.ovpn"
    file_path.write_text(ovpn_stdout.decode())

    return file_path
