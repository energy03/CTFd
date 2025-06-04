from docker import client
from os import getenv

DOCKER_API_URL = getenv("DOCKER_API_URL")

CLIENT = client.DockerClient(base_url=DOCKER_API_URL)

def start_container(image: str, container_name: str, ports: dict = None):
    try:
        container = CLIENT.containers.run(image, name=container_name, detach=True, remove=True, ports=ports)
        return container
    except Exception as e:
        return None

def restart_container(container_name: str):
    try:
        container = CLIENT.containers.get(container_name)
        container.restart()
        return True
    except Exception as e:
        return False

def stop_container(container_name: str):
    try:
        container = CLIENT.containers.get(container_name)
        container.stop()
        return True
    except Exception as e:
        return False
    
def get_image(image_name: str):
    try:
        image = CLIENT.images.get(image_name)
        return image
    except Exception as e:
        return None