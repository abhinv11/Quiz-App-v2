from flask_jwt_extended import JWTManager
from application.models import User, Role

jwt = JWTManager()

@jwt.user_identity_loader
def load(identity):
    # If identity is already a string (email), return it as-is
    # If identity is a User object, return the email
    if isinstance(identity, str):
        return identity
    return identity.email

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data['sub']
    return User.query.filter_by(email=identity).one_or_none()