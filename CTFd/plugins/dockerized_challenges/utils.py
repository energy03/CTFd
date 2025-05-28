from docker import client

DOCKER_API_URL = "URL"

CLIENT = client.DockerClient(base_url=DOCKER_API_URL)

def start_container(image: str, container_name: str):
    try:
        container = CLIENT.containers.run(image, name=container_name, detach=True, remove=True)
        if container:
            return True
        else:
            return False
    except Exception as e:
        return False

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