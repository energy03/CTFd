from typing import List  # noqa: I001

from flask import abort, render_template, request, url_for
from flask_restx import Namespace, Resource
from sqlalchemy.sql import and_

from CTFd.api.v1.helpers.request import validate_args
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import APIDetailedSuccessResponse, APIListSuccessResponse
from CTFd.cache import clear_challenges, clear_standings
from CTFd.constants import RawEnum
from CTFd.exceptions.challenges import (
    ChallengeCreateException,
    ChallengeUpdateException,
)
from CTFd.models import ChallengeFiles as ChallengeFilesModel
from CTFd.models import Challenges
from CTFd.models import ChallengeTopics as ChallengeTopicsModel
from CTFd.models import Fails, Flags, Hints, HintUnlocks, Solves, Submissions, Tags, db
from CTFd.plugins.challenges import CHALLENGE_CLASSES, get_chal_class
from CTFd.schemas.challenges import ChallengeSchema
from CTFd.schemas.flags import FlagSchema
from CTFd.schemas.hints import HintSchema
from CTFd.schemas.tags import TagSchema
from CTFd.utils import config, get_config
from CTFd.utils import user as current_user
from CTFd.utils.challenges import (
    get_all_challenges,
    get_solve_counts_for_challenges,
    get_solve_ids_for_user_id,
    get_solves_for_challenge_id,
)
from CTFd.utils.config.visibility import (
    accounts_visible,
    challenges_visible,
    scores_visible,
)
from CTFd.utils.dates import ctf_ended, ctf_paused, ctftime
from CTFd.utils.decorators import (
    admins_only,
    during_ctf_time_only,
    require_verified_emails,
)
from CTFd.utils.decorators.visibility import (
    check_account_visibility,
    check_challenge_visibility,
    check_score_visibility,
)
from CTFd.utils.humanize.words import pluralize
from CTFd.utils.logging import log
from CTFd.utils.security.signing import serialize
from CTFd.utils.user import (
    authed,
    get_current_team,
    get_current_team_attrs,
    get_current_user,
    get_current_user_attrs,
    is_admin,
)

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
        # TODO logic to start instance
        # This is a placeholder for the actual logic to start the instance
        
        return {"success": True, "data": {"message": "Instance started successfully"}}
    
    
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
        # TODO logic to restart instance
        # This is a placeholder for the actual logic to restart the instance
        
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
        # TODO logic to stop instance
        # This is a placeholder for the actual logic to stop the instance
        
        return {"success": True, "data": {"message": "Instance stopped successfully"}}