from docker import client
from docker.models.containers import Container

DOCKER_API_URL = "URL"

CLIENT = client.DockerClient(base_url=DOCKER_API_URL)

def start_container(image: str):
    try:
        container = CLIENT.containers.run(image, detach=True, remove=True)
        return container
    except Exception as e:
        return None

def restart_container(container: Container):
    try:
        container.restart()
        return True
    except Exception as e:
        return False

def stop_container(container: Container):
    try:
        container.stop()
        return True
    except Exception as e:
        return False