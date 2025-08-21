from flask import Flask
from werkzeug.security import generate_password_hash
from application.config import LocalDevelopmentConfig
from application.database import db
from application.models import User, Role, UserRoles, Student, Subject, Chapter, Quiz
from application.security import jwt
from flask_cors import CORS
from application.celery_init import celery_init_app
from celery.schedules import crontab

app = None

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    jwt.init_app(app)
    app.app_context().push()
    return app

app = create_app()
celery = celery_init_app(app)
celery.autodiscover_tasks()

from application.routes import *

@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab('*/2'),
        Monthly_report.s(),
    )

if __name__ == "__main__":
    db.create_all()
    
    # Create default roles first - only admin and student
    admin_role = Role.query.filter_by(name='admin').first()
    if not admin_role:
        admin_role = Role(name='admin', description='Administrator/Teacher role')
        db.session.add(admin_role)
    
    student_role = Role.query.filter_by(name='student').first()
    if not student_role:
        student_role = Role(name='student', description='Student role')
        db.session.add(student_role)
    
    # Commit roles first
    db.session.commit()
    
    # Create users
    admin_user = User.query.filter_by(email='admin@mail.com').first()
    if not admin_user:
        admin_user = User(email='admin@mail.com', password=generate_password_hash('admin123'))
        admin_user.roles.append(admin_role)
        db.session.add(admin_user)
    
    student_user = User.query.filter_by(email='student_1@mail.com').first()
    if not student_user:
        student_user = User(email='student_1@mail.com', password='student123')
        student_user.roles.append(student_role)  # Explicitly assign student role
        db.session.add(student_user)
        db.session.commit()  # Commit to get the user ID
        
        # Create student profile after user is committed
        from datetime import date
        student_profile = Student(
            user_id=student_user.id,
            name="Student One",
            dob=date(2000, 1, 1),
            qualification="Graduate"
        )
        db.session.add(student_profile)

    db.session.commit()
    app.run()
