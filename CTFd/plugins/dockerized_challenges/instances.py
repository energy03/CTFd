from flask import request, make_response
from flask_restx import Namespace, Resource
from CTFd.models import Challenges, Flags
from CTFd.models import db
from CTFd.schemas.challenges import ChallengeSchema
from CTFd.utils.decorators import admins_only, during_ctf_time_only, require_verified_emails
from CTFd.utils.decorators.visibility import check_challenge_visibility
from .utils import (
    get_chall_token,
    get_image,
    start_container,
    restart_container,
    stop_container,
    build_image_from_tar,
    request_certificates,
)
from CTFd.utils.logging import log
import os

DOMAIN = os.getenv("CHALLENGES_DOMAIN")

instances_namespace = Namespace(
    "instances", description="Endpoint to manage instances of Dockerized challenges"
)


@instances_namespace.route("/start")
class ChallengeInstanceStart(Resource):
    @admins_only
    @instances_namespace.doc(
        description="Endpoint to start an instance of a Dockerized challenge",
        responses={
            200: (
                "Success",
                "APISimpleSuccessResponse",
            ),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def post(self):
        data = request.form or request.get_json()

        # Load data through schema for validation but not for insertion
        schema = ChallengeSchema()
        response = schema.load(data)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        challenge_id = data.get("challenge_id")
        challenge = Challenges.query.filter_by(id=challenge_id).first()
        
        if not challenge:
            return {"success": False, "errors": {"challenge_id": ["Challenge not found"]}}, 404
        
        challenge_type = challenge.type
        
        if challenge_type != "dockerized":
            return {"success": False, "errors": {"challenge_id": ["Challenge is not a Dockerized challenge"]}}, 400
        
        # Verify if the instance is already running
        if challenge.is_running:
            challenge.is_running = True
            db.session.add(challenge)
            db.session.commit()
            return {"success": False, "errors": {"challenge_id": ["Challenge instance is already running"]}}, 400
        
        # Get the image
        image = get_image(challenge.image)

        if not image:
            return {"success": False, "errors": {"image": ["Docker image not found"]}}, 404
        
        # Get the exposed ports list of the image
        exposed_ports = list(image.attrs.get("Config", {}).get("ExposedPorts", {}).keys())
        flags = Flags.query.filter_by(challenge_id=challenge_id).all()
        env = {}
        acc = 1
        for flag in flags:
            env[f"FLAG{acc}"] = flag.content
            acc+=1 

        ports = {}
        if len(exposed_ports) == 1 and challenge.port:
            if challenge.protocol == "http":
                ports = { exposed_ports[0]: ("127.0.0.1", challenge.port) }
            else:
                ports = { exposed_ports[0]: ("0.0.0.0", challenge.port) }
        
        container = start_container(image, challenge.container, ports=ports, env=env)

        chall_name = f"chall{challenge.id}"
        
        if container:
            ## Update challenge instance status
            challenge.is_running = True
            db.session.add(challenge)
            db.session.commit()

            # Return the response with a Set-Cookie header
            response = make_response({ "success": True, "data": {"message": "Instance started successfully"}})

            if challenge.protocol == "http":
                chall_token = get_chall_token(chall_name)
                response.set_cookie(
                    f"{chall_name}_token",
                    chall_token,
                    max_age=None,  # Session cookie
                    httponly=True,
                    secure=False,  # Use secure cookies in production
                    samesite="Lax",  # Adjust as needed
                    domain=f".{DOMAIN}",
                )

            return response
        else:
            return {"success": False, "errors": "Internal Error"}, 500


    
@instances_namespace.route("/restart")
class ChallengeInstanceRestart(Resource):
    @admins_only
    @instances_namespace.doc(
        description="Endpoint to restart an instance of a Dockerized challenge",
        responses={
            200: (
                "Success",
                "APISimpleSuccessResponse",
            ),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def post(self):
        data = request.form or request.get_json()

        # Load data through schema for validation but not for insertion
        schema = ChallengeSchema()
        response = schema.load(data)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        challenge_id = data.get("challenge_id")
        challenge = Challenges.query.filter_by(id=challenge_id).first()
        if not challenge:
            return {"success": False, "errors": {"challenge_id": ["Challenge not found"]}}, 404
        
        challenge_type = challenge.type
        
        if challenge_type != "dockerized":
            return {"success": False, "errors": {"challenge_id": ["Challenge is not a Dockerized challenge"]}}, 400
        
        # Verify if the instance is running
        if not challenge.is_running:
            challenge.is_running = False
            db.session.add(challenge)
            db.session.commit()
            return {"success": False, "errors": {"challenge_id": ["Challenge instance is not running"]}}, 400
        
        # Restart the container
        if not restart_container(challenge.container):
            return {"success": False, "errors": "Internal Error"}, 500
        
        return {"success": True, "data": {"message": "Instance restarted successfully"}}
    
@instances_namespace.route("/stop")
class ChallengeInstanceStop(Resource):
    @admins_only
    @instances_namespace.doc(
        description="Endpoint to stop an instance of a Dockerized challenge",
        responses={
            200: (
                "Success",
                "APISimpleSuccessResponse",
            ),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def post(self):
        data = request.form or request.get_json()

        # Load data through schema for validation but not for insertion
        schema = ChallengeSchema()
        response = schema.load(data)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        challenge_id = data.get("challenge_id")
        challenge = Challenges.query.filter_by(id=challenge_id).first()
        if not challenge:
            return {"success": False, "errors": {"challenge_id": ["Challenge not found"]}}, 404
        challenge_type = challenge.type
        
        if challenge_type != "dockerized":
            return {"success": False, "errors": {"challenge_id": ["Challenge is not a Dockerized challenge"]}}, 400
        
        # Verify if the instance is running
        if not challenge.is_running:
            challenge.is_running = False
            db.session.add(challenge)
            db.session.commit()
            # If the instance is not running, return an error
            return {"success": False, "errors": {"challenge_id": ["Challenge instance is not running"]}}, 400
        
        # Stop the container
        if not stop_container(challenge.container):
            return {"success": False, "errors": "Internal Error"}, 500
        
        # Update challenge instance status
        challenge.is_running = False
        db.session.add(challenge)
        db.session.commit()

        return {"success": True, "data": {"message": "Instance stopped successfully"}}
    

# Route To build the image, being given the challenge id and a tar file with the Dockerfile and other files
@instances_namespace.route("/build")
class ChallengeInstanceBuild(Resource):
    @admins_only
    @instances_namespace.doc(
        description="Endpoint to build an instance of a Dockerized challenge",
        responses={
            200: (
                "Success",
                "APISimpleSuccessResponse",
            ),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def post(self):
        data = request.form or request.get_json()

        # Load data through schema for validation but not for insertion
        schema = ChallengeSchema()
        response = schema.load(data)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        challenge_id = data.get("challenge_id")
        challenge = Challenges.query.filter_by(id=challenge_id).first()
        
        if not challenge:
            return {"success": False, "errors": {"challenge_id": ["Challenge not found"]}}, 404
        
        challenge_type = challenge.type
        
        if challenge_type != "dockerized":
            return {"success": False, "errors": {"challenge_id": ["Challenge is not a Dockerized challenge"]}}, 400
        
        # Get the tar file from the request
        tar_file = request.files.get("tar_file")

        if not tar_file:
            return {"success": False, "errors": {"tar_file": ["Tar file is required"]}}, 400
        
        tar_file_content = tar_file.stream

        # TODO check the mime type and the magic header to see if it is a valid tar file
        # TODO check if Dockerfile expose only one port

        try:
            image = build_image_from_tar(tar_file_content, challenge.image)
            if not image:
                return {"success": False, "errors": {"image": ["Error building Docker image"]}}, 500
            else:
                return {"success": True, "data": {"message": "Image built successfully"}}
        except Exception as e:
            return {"success": False, "errors": {"image": ["Error building Docker image"]}, "msg": e.__str__() }, 500

@instances_namespace.route("/join")
class ChallengeInstanceJoin(Resource):
    @check_challenge_visibility
    @during_ctf_time_only
    @require_verified_emails
    @instances_namespace.doc(
        description="Endpoint to join a Dockerized challenge",
        responses={
            200: (
                "Success",
                "APISimpleSuccessResponse",
            ),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def post(self):
        data = request.form or request.get_json()

        # Load data through schema for validation but not for insertion
        schema = ChallengeSchema()
        response = schema.load(data)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        challenge_id = data.get("challenge_id")
        challenge = Challenges.query.filter_by(id=challenge_id).first()
        
        if not challenge:
            return {"success": False, "errors": {"challenge_id": ["Challenge not found"]}}, 404
        
        challenge_type = challenge.type
        
        if challenge_type != "dockerized":
            return {"success": False, "errors": {"challenge_id": ["Challenge is not a Dockerized challenge"]}}, 400
        
        chall_name = f"chall{challenge.id}"
        token = get_chall_token(chall_name)
        response = make_response({
            "success": True,
            "data": {
                "status": "joined",
                "message": "Successfully joined the challenge",
                "url": challenge.connection_info
            }
        })
        response.set_cookie(
            f"{chall_name}_token",
            token,
            max_age=None,  # Session cookie
            httponly=True,
            secure=False,  # TODO Use secure cookies in production
            samesite="Lax",  # Adjust as needed
            domain=f".{DOMAIN}",
        )

        return response

@instances_namespace.route("/certificates")
class ChallengeCertificatesRequest(Resource):
    @admins_only
    @instances_namespace.doc(
        description="Endpoint to request a Dockerized challenges SSL/TLS certificates",
        responses={
            200: (
                "Success",
                "APISimpleSuccessResponse",
            ),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def get(self):
        try:
            success, errors, status = request_certificates()
            if success:
                return {"success": True, "data": {"message": "Certificates requested successfully"}}
            else:
                return {"success": False, "errors": errors}, status
        except Exception as e:
            return {"success": False, "errors": {"certificates": f"{[str(e)]}"}}, 500