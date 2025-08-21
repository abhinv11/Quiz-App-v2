class Config():
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class LocalDevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///quizappDb.sqlite3"
    JWT_SECRET_KEY = 'your_jwt_secret_key_here'
    SECURITY_PASSWORD_HASH = 'bcrypt'