from pathlib import Path
from CTFd.utils.plugins import override_template
from flask import Blueprint
from CTFd.models import Challenges, db
from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.challenges import CHALLENGE_CLASSES, BaseChallenge
from CTFd.plugins.dynamic_challenges import DynamicValueChallenge
from CTFd.plugins.migrations import upgrade
from CTFd.api import CTFd_API_v1
from CTFd.plugins.dockerized_challenges.instances import instances_namespace
from CTFd.api.v1.challenges import ChallengeList
from CTFd.plugins.dockerized_challenges.api.challenges import create_challenge

class DockerizedChallenge(Challenges):
    __mapper_args__ = {"polymorphic_identity": "dockerized"}
    id = db.Column(
        db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE"), primary_key=True
    )
    is_dynamic = db.Column(db.Boolean, default=False)
    initial = db.Column(db.Integer, default=0)
    minimum = db.Column(db.Integer, default=0)
    decay = db.Column(db.Integer, default=0)
    function = db.Column(db.String(32), default="logarithmic")
    image = db.Column(db.String(32), default=None)
    container = db.Column(db.String(64), default=None)
    port = db.Column(db.Integer, default=None)
    is_running = db.Column(db.Boolean, default=False)

    def __init__(self, *args, **kwargs):
        super(DockerizedChallenge, self).__init__(**kwargs)
        
        if kwargs["is_dynamic"]:
            self.value = kwargs["initial"]
        else:
            self.initial = kwargs["value"]
            self.minimum = kwargs["value"]
            self.decay = 0                    
            # except KeyError:
            #     raise ChallengeCreateException("Missing initial value for challenge")


class CTFdDockerizedChallenge(BaseChallenge):
    id = "dockerized"  # Unique identifier used to register challenges
    name = "dockerized"  # Name of a challenge type
    templates = (
        {  # Handlebars templates used for each aspect of challenge editing & viewing
            "create": "/plugins/dockerized_challenges/assets/create.html",
            "update": "/plugins/dockerized_challenges/assets/update.html",
            "view": "/plugins/dockerized_challenges/assets/view.html",
            "challenge": "/plugins/dockerized_challenges/assets/challenge.html"
        }
    )
    scripts = {  # Scripts that are loaded when a template is loaded
        "create": "/plugins/dockerized_challenges/assets/create.js",
        "update": "/plugins/dockerized_challenges/assets/update.js",
        "view": "/plugins/dockerized_challenges/assets/view.js",
        "challenge": "/plugins/dockerized_challenges/assets/challenge.js"
    }
    # Route at which files are accessible. This must be registered using register_plugin_assets_directory()
    route = "/plugins/dockerized_challenges/assets/"
    # Blueprint used to access the static_folder directory.
    blueprint = Blueprint(
        "dockerized_challenges",
        __name__,
        template_folder="templates",
        static_folder="assets",
    )
    challenge_model = DockerizedChallenge

    # @classmethod
    # def calculate_value(cls, challenge):
    #     f = DECAY_FUNCTIONS.get(challenge.function, logarithmic)
    #     value = f(challenge)

    #     challenge.value = value
    #     db.session.commit()
    #     return challenge

    @classmethod
    def read(cls, challenge):
        """
        This method is in used to access the data of a challenge in a format processable by the front end.

        :param challenge:
        :return: Challenge object, data dictionary to be returned to the user
        """
        challenge = DockerizedChallenge.query.filter_by(id=challenge.id).first()
        data = super().read(challenge)
        
        data.update(
            {
                "is_dynamic": challenge.is_dynamic, 
                "initial": challenge.initial if challenge.is_dynamic else 0,
                "decay": challenge.decay if challenge.is_dynamic else 0,
                "minimum": challenge.minimum if challenge.is_dynamic else 0,
                "function": challenge.function if challenge.is_dynamic else None,
            }
        )
        
        return data

    @classmethod
    def solve(cls, user, team, challenge, request):
        super().solve(user, team, challenge, request)
        if challenge.is_dynamic:
            DynamicValueChallenge.calculate_value(challenge)



def load(app):
    upgrade(plugin_name="dockerized_challenges")
    CHALLENGE_CLASSES["dockerized"] = CTFdDockerizedChallenge
    register_plugin_assets_directory(
        app, base_path="/plugins/dockerized_challenges/assets/"
    )
    
    # Override default templates for challenge and challenges pages of admin theme
    dir_path = Path(__file__).parent.resolve()
    template_challenge_path = dir_path / 'templates' / 'challenge.html'
    template_challenges_path = dir_path / 'templates' / 'challenges.html'
    override_template('admin/challenges/challenge.html', open(template_challenge_path).read())
    override_template('admin/challenges/challenges.html', open(template_challenges_path).read())
    
    # Register the API namespace
    CTFd_API_v1.add_namespace(instances_namespace, "/dockerized_challenges/instances")

    # Register the blueprint for the challenge type
    app.register_blueprint(
        CTFdDockerizedChallenge.blueprint,
        url_prefix=CTFdDockerizedChallenge.route,
    )

    # Override challenge creation logic
    ChallengeList.post = create_challenge