from flask import request
from CTFd.cache import clear_challenges
from CTFd.exceptions.challenges import ChallengeCreateException
from CTFd.plugins.challenges import get_chal_class
from CTFd.schemas.challenges import ChallengeSchema
from CTFd.plugins.dockerized_challenges.utils import create_nginx_vhost_conf


def create_challenge(self):
    data = request.form or request.get_json()

    # Load data through schema for validation but not for insertion
    schema = ChallengeSchema()
    response = schema.load(data)
    if response.errors:
        return {"success": False, "errors": response.errors}, 400

    challenge_type = data.get("type", "standard")

    challenge_class = get_chal_class(challenge_type)
    try:
        challenge = challenge_class.create(request)
    except ChallengeCreateException as e:
        return {"success": False, "errors": {"": [str(e)]}}, 500

    response = challenge_class.read(challenge)

    chall_name = f"chall{challenge.id}"

    clear_challenges()

    if challenge.type == "dockerized":
        create_nginx_vhost_conf(chall_name, challenge.port)

    return {"success": True, "data": response}