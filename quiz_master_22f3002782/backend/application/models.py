from flask_security import UserMixin, RoleMixin
from datetime import datetime
import uuid
import enum
from .database import db

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, default=True)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    roles = db.relationship('Role', backref='bearers', secondary='user_roles')

    # Relationships
    student_profile = db.relationship('Student', backref='user', uselist=False)
    quiz_attempts = db.relationship('Score', backref='user', lazy=True)
    user_answers = db.relationship('UserAnswer', backref='user', lazy=True)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))


class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    qualification = db.Column(db.String(255), nullable=False)


# Define the Subject model
class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Relationships
    chapters = db.relationship('Chapter', backref='subject', lazy=True)

# Define the Chapter model
class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Relationships
    quizzes = db.relationship('Quiz', backref='chapter', lazy=True)

# Define the Quiz model
class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date_of_quiz = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    time_duration = db.Column(db.Integer, nullable=False)  # Duration in minutes
    remarks = db.Column(db.Text, nullable=True)
    is_published = db.Column(db.Boolean, default=False)

    # Relationships
    questions = db.relationship('Question', backref='quiz', lazy=True)
    scores = db.relationship('Score', backref='quiz', lazy=True)

# Question type enum
class QuestionType(enum.Enum):
    MCQ = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    FILL_BLANK = "fill_blank"

# Define the Question model
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_statement = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.Enum(QuestionType), nullable=False)
    points = db.Column(db.Integer, default=1)
    
    # For MCQ questions
    option1 = db.Column(db.String(255), nullable=True)
    option2 = db.Column(db.String(255), nullable=True)
    option3 = db.Column(db.String(255), nullable=True)
    option4 = db.Column(db.String(255), nullable=True)
    
    # For all question types
    correct_answer = db.Column(db.Text, nullable=False)  # For MCQ: 'option1', 'option2', etc. For T/F: 'true' or 'false'. For others: the correct text
    
    # Relationships
    user_answers = db.relationship('UserAnswer', backref='question', lazy=True)

# Define the Score model
class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    time_stamp_of_attempt = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    total_scored = db.Column(db.Integer, nullable=False)
    total_possible = db.Column(db.Integer, nullable=False)
    completion_time = db.Column(db.Integer, nullable=True)  # Time taken in seconds
    
    # Relationships
    user_answers = db.relationship('UserAnswer', backref='score', lazy=True)

# Define the UserAnswer model to track user responses
class UserAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score_id = db.Column(db.Integer, db.ForeignKey('score.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_answer = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    points_earned = db.Column(db.Integer, nullable=False)