from typing import IO
from docker import client
from paramiko import SSHClient
import os
import re
import secrets
from CTFd.utils.logging import log
from shlex import quote


# If the environment variable DOCKER_API_URL is not set, get DOCKER_API_USER and DOCKER_API_HOST
DOCKER_API_URL = os.getenv("DOCKER_API_URL")

if not DOCKER_API_URL:
    DOCKER_API_USER = os.getenv("DOCKER_API_USER")
    DOCKER_API_HOST = os.getenv("DOCKER_API_HOST")
    DOCKER_API_URL = f"ssh://{DOCKER_API_USER}@{DOCKER_API_HOST}"

CLIENT = client.DockerClient(base_url=DOCKER_API_URL)

SSHCLIENT = SSHClient()
SSHCLIENT.load_system_host_keys()
SSHCLIENT.connect(
    hostname=os.getenv("DOCKER_API_HOST"), username=os.getenv("DOCKER_API_USER")
)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
NGINX_VHOST_CONF_TEMPLATE = ""
with open(os.path.join(CURRENT_DIR, "challenge_nginx/vhost.conf"), "r") as f:
    NGINX_VHOST_CONF_TEMPLATE = f.read()

DOMAIN = os.getenv("CHALLENGES_DOMAIN")

NGINX_CONF_DIRECTORY = "/etc/nginx/sites-available/"
NGINX_LINK_DIRECTORY = "/etc/nginx/sites-enabled/"
NGINX_CHALL_TOKEN_FILE = "/etc/nginx/sites-tokens/expected_tokens"

## Create the file remotely on the SSH server


def create_nginx_vhost_conf(challenge_name: str, port: int):
    try:
        fqdn = f"{challenge_name}.{DOMAIN}"
        nginx_conf = NGINX_VHOST_CONF_TEMPLATE.format(
            server_name=fqdn,
            chall=challenge_name,
            token_variables=NGINX_CHALL_TOKEN_FILE,
            port=port,
        )

        with SSHCLIENT.open_sftp() as sftp:
            conf_file = f"{NGINX_CONF_DIRECTORY}{fqdn}"
            conf_link = f"{NGINX_LINK_DIRECTORY}{fqdn}"

            with sftp.file(conf_file, "w") as f:
                f.write(nginx_conf)
            f.flush()
            f.close()
            # Delete the symlink if it exists
            try:
                sftp.remove(conf_link)
            except FileNotFoundError:
                pass

            # TODO Filter entries to avoid command execution
            filtered_conf_file = quote(conf_file)
            SSHCLIENT.exec_command(f"ln -s {filtered_conf_file} {NGINX_LINK_DIRECTORY}")

            update_token(challenge_name)

            # Reload Nginx to apply the new configuration
            command = "sudo /bin/systemctl reload nginx"

            _, stdout, _ = SSHCLIENT.exec_command(command)
            exit_status = (
                stdout.channel.recv_exit_status()
            )  # Wait for command to finish

            if exit_status != 0:
                return False

            return True
    except Exception:
        return False


def start_container(image: str, container_name: str, ports: dict = None, env = None):
    try:
        container = CLIENT.containers.run(
            image, name=container_name, detach=True, remove=True, ports=ports, environment=env
        )
        return container
    except Exception:
        return None


def restart_container(container_name: str):
    try:
        container = CLIENT.containers.get(container_name)
        container.restart()
        return True
    except Exception:
        return False


def stop_container(container_name: str):
    try:
        container = CLIENT.containers.get(container_name)
        container.stop()
        return True
    except Exception:
        return False


def get_image(image_name: str):
    try:
        image = CLIENT.images.get(image_name)
        return image
    except Exception:
        return None


# Build an image from a tar file content
def build_image_from_tar(tar_content: IO[bytes], image_name: str):
    ## Do it via SSH
    try:
        with SSHCLIENT.open_sftp() as sftp:
            tar_file_path = f"/tmp/{image_name}.tar"
            with sftp.file(tar_file_path, "wb") as tar_file:
                tar_file.write(tar_content.read())
                tar_file.flush()
                tar_file.close()

            # Build the image using the tar file
            build_command = f"docker build -t {image_name} - < {tar_file_path}"
            _, stdout, _ = SSHCLIENT.exec_command(build_command)
            exit_status = (
                stdout.channel.recv_exit_status()
            )  # Wait for command to finish

            if exit_status == 0:
                return True
            else:
                return False
    except Exception as e:
        log(f"Error building image from tar: {e}")
        return False


def get_chall_token(chall_name: str):
    tokens = load_conf()
    varname = f"expected_token_{chall_name}"
    if varname in tokens:
        return tokens[varname]
    else:
        return None


def load_conf():
    tokens = {}
    with SSHCLIENT.open_sftp() as sftp:
        with sftp.file(NGINX_CHALL_TOKEN_FILE, "r") as f:
            for line in f:
                match = re.match(
                    r'set\s+\$(expected_token_\S+)\s+"([^"]+)";', line.strip()
                )
                if match:
                    tokens[match.group(1)] = match.group(2)

    return tokens


def save_conf(tokens):
    with SSHCLIENT.open_sftp() as sftp:
        with sftp.file(NGINX_CHALL_TOKEN_FILE, "w") as f:
            for varname, token in tokens.items():
                f.write(f'set ${varname} "{token}";\n')
            f.flush()
            f.close()


def generate_token():
    return secrets.token_urlsafe(32)


def update_token(chall_name):
    tokens = load_conf()
    varname = f"expected_token_{chall_name}"
    new_token = generate_token()
    tokens[varname] = new_token
    save_conf(tokens)
    return new_token


def remove_token(chall_name):
    tokens = load_conf()
    varname = f"expected_token_{chall_name}"
    if varname in tokens:
        del tokens[varname]
        save_conf(tokens)

def request_certificates():
    try:
        flag = ''
        with SSHCLIENT.open_sftp() as sftp:
            # Look for filenames in NGINX_LINK_DIRECTORY that match _____.{DOMAIN}
            filenames = sftp.listdir(NGINX_LINK_DIRECTORY)
            if not filenames:
                return False, {"error": "1 No files found in NGINX_LINK_DIRECTORY"}, 404
            for filename in filenames:
                if filename.endswith(f'.{DOMAIN}') and not filename.startswith("."):
                    flag += f"-d {filename} "
            
        if not flag:
            return False, {"error": "No valid domain to request certificate for"}, 404
        
        # Request the certificate using certbot --nginx
        command = f"sudo /usr/bin/certbot --nginx {flag} --non-interactive --agree-tos --expand"
        _, stdout,sterr = SSHCLIENT.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()  # Wait for command to finish
        if exit_status != 0:
            return False, {"error": f"3 {sterr.read().decode()}"}, 500
        return True, None, None

    except Exception as e:
        return False, {"error": f"4 {str(e)}"}, 500
