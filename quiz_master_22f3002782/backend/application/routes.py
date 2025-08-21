from flask import current_app as app, jsonify, request, abort, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from application.models import User, Role, Student, Subject, Chapter, Quiz, Question, QuestionType, Score, UserAnswer
from application.database import db
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from functools import wraps
from datetime import datetime, date
import uuid
import enum
from celery.result import AsyncResult
from .tasks import download_csv_report, Monthly_report, quiz_remainder

# --- Provided Code (from user) ---

def role_required(role):
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_email = get_jwt_identity()
            current_user = User.query.filter_by(email=current_user_email).first()
            
            if not current_user:
                return jsonify(message="User not found"), 404
            
            user_roles = [r.name for r in current_user.roles]
            print(f"User roles: {user_roles}, Required role: {role}")  # Debug line
            
            if role not in user_roles:
                return jsonify(message=f"{role.capitalize()}s only!"), 403
            
            return fn(*args, **kwargs)
        return decorated_function
    return wrapper

@app.route('/api/login', methods=['POST'])
def login():
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    
    print(f"Login attempt - Email: {email}, Password: {password}")

    user = User.query.filter_by(email=email).one_or_none()
    if not user:
        print(f"User not found for email: {email}")
        return jsonify(message="Wrong email or password"), 404
    
    print(f"User found: {user.email}, Stored password: {user.password}")
    print(f"User roles: {[role.name for role in user.roles]}")
    
    # Check if password is hashed or plain text and verify accordingly
    if user.password.startswith('pbkdf2:sha256:') or user.password.startswith('scrypt:'):
        # Password is hashed, use check_password_hash
        print("Checking hashed password...")
        if not check_password_hash(user.password, password):
            print("Hashed password check failed")
            return jsonify(message="Wrong email or password"), 404
    else:
        # Password is plain text (for existing users like student_1)
        print("Checking plain text password...")
        if user.password != password:
            print(f"Plain text password check failed. Expected: {user.password}, Got: {password}")
            return jsonify(message="Wrong email or password"), 404

    print("Password verification successful!")
    # Pass the email as identity instead of the user object
    access_token = create_access_token(identity=user.email)
    return jsonify(access_token=access_token), 200

@app.route('/api/register', methods=['POST'])
def register():
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    name = request.json.get('name', None)
    dob = request.json.get('dob', None)
    qualification = request.json.get('qualification', None)

    if not email or not password or not name or not dob or not qualification:
        return jsonify(message="Missing required fields"), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify(message="User already exists"), 409

    # Create new user
    new_user = User(email=email, password=generate_password_hash(password))
    
    # Get the student role and assign it to the new user
    student_role = Role.query.filter_by(name='student').first()
    if student_role:
        new_user.roles.append(student_role)
    
    db.session.add(new_user)
    db.session.commit()  # Commit to get the user ID

    # Convert date string to Python date object
    try:
        # Try different date formats
        if '/' in dob:
            dob_date = datetime.strptime(dob, '%d/%m/%Y').date()
        elif '-' in dob:
            dob_date = datetime.strptime(dob, '%Y-%m-%d').date()
        else:
            return jsonify(message="Invalid date format. Use DD/MM/YYYY or YYYY-MM-DD"), 400
    except ValueError:
        return jsonify(message="Invalid date format. Use DD/MM/YYYY or YYYY-MM-DD"), 400

    # Create student profile
    student_profile = Student(
        user_id=new_user.id, 
        name=name, 
        dob=dob_date, 
        qualification=qualification
    )
    db.session.add(student_profile)
    db.session.commit()

    return jsonify(message="User registered successfully", user_id=new_user.id), 201


@app.route('/api/me', methods=['GET']) # Renamed from /profile to match API list
@jwt_required()
def get_current_user_profile():
    # Get the user identity from JWT token
    current_user_email = get_jwt_identity()
    
    # Query the user from database
    current_user = User.query.filter_by(email=current_user_email).first()
    
    if not current_user:
        return jsonify(message="User not found"), 404
    
    user_data = {
        'id': current_user.id,
        'email': current_user.email,
        'active': current_user.active,
        'roles': [role.name for role in current_user.roles]
    }
    
    if current_user.student_profile:
        user_data['student_profile'] = {
            'name': current_user.student_profile.name,
            'dob': current_user.student_profile.dob.isoformat(),
            'qualification': current_user.student_profile.qualification
        }
    
    return jsonify(user=user_data), 200

# NOTE: /dashboard and /onlyadmin are kept for reference but are not part of the RESTful API list.
@app.route("/dashboard", methods=['GET'])
@jwt_required()
def dashboard():
    current_user_email = get_jwt_identity()
    current_user = User.query.filter_by(email=current_user_email).first()
    if not current_user:
        return jsonify(message="User not found"), 404
    user_roles = [role.name for role in current_user.roles]
    if 'admin' in user_roles:
        return jsonify(message='Welcome to the admin dashboard!'), 200
    else:
        return jsonify(message='Welcome to the student dashboard!'), 200
    
# @app.route("/onlyadmin", methods=['GET'])
# @role_required('admin')
# def only_admin():
#     return jsonify(message='Welcome to the admin-only area!'), 200

# --- New Endpoints ---

# I. Authentication & Authorization Endpoints (Completion)

@app.route('/api/logout', methods=['POST'])
@jwt_required()
def logout():
    # For JWT, logout is typically handled client-side by deleting the token.
    # Server-side invalidation would require a blacklist mechanism, which is
    # beyond the scope of a basic implementation but good to consider for production.
    return jsonify(message="Successfully logged out"), 200

# II. Administrator Endpoints

# A. User Management

@app.route('/api/admin/users', methods=['GET'])
@role_required('admin')
def admin_get_all_users():
    users = User.query.all()
    output = []
    for user in users:
        user_data = {
            'id': user.id,
            'email': user.email,
            'active': user.active,
            'roles': [role.name for role in user.roles]
        }
        if user.student_profile:
            user_data['student_profile'] = {
                'name': user.student_profile.name,
                'dob': user.student_profile.dob.isoformat() if user.student_profile.dob else None,
                'qualification': user.student_profile.qualification
            }
        output.append(user_data)
    return jsonify(users=output), 200

@app.route('/api/admin/users/<int:user_id>', methods=['GET'])
@role_required('admin')
def admin_get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        abort(404, description="User not found")
    
    user_data = {
        'id': user.id,
        'email': user.email,
        'active': user.active,
        'roles': [role.name for role in user.roles]
    }
    if user.student_profile:
        user_data['student_profile'] = {
            'name': user.student_profile.name,
            'dob': user.student_profile.dob.isoformat() if user.student_profile.dob else None,
            'qualification': user.student_profile.qualification
        }
    return jsonify(user=user_data), 200

@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@role_required('admin')
def admin_update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        abort(404, description="User not found")
    
    data = request.get_json()
    if 'email' in data:
        user.email = data['email']
    if 'active' in data:
        user.active = data['active']
    if 'password' in data and data['password']:
        user.password = generate_password_hash(data['password'])
    
    # Update roles
    if 'roles' in data and isinstance(data['roles'], list):
        user.roles = [] # Clear existing roles
        for role_name in data['roles']:
            role = Role.query.filter_by(name=role_name).first()
            if role:
                user.roles.append(role)
    
    # Update student profile if it exists
    if user.student_profile:
        if 'name' in data:
            user.student_profile.name = data['name']
        if 'dob' in data:
            try:
                if '/' in data['dob']:
                    user.student_profile.dob = datetime.strptime(data['dob'], '%d/%m/%Y').date()
                elif '-' in data['dob']:
                    user.student_profile.dob = datetime.strptime(data['dob'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify(message="Invalid date format for DOB. Use DD/MM/YYYY or YYYY-MM-DD"), 400
        if 'qualification' in data:
            user.student_profile.qualification = data['qualification']
    
    db.session.commit()
    return jsonify(message="User updated successfully"), 200

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@role_required('admin')
def admin_delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        abort(404, description="User not found")
    
    # Delete associated student profile if it exists
    if user.student_profile:
        db.session.delete(user.student_profile)
    
    # Delete associated scores and user answers
    for score in user.quiz_attempts:
        for user_answer in score.user_answers:
            db.session.delete(user_answer)
        db.session.delete(score)
    
    for user_answer in user.user_answers: # Catch any direct user_answers not linked via score
        if user_answer.score_id is None: # Only delete if not already deleted via score
            db.session.delete(user_answer)

    db.session.delete(user)
    db.session.commit()
    return jsonify(message="User deleted successfully"), 200

@app.route('/api/admin/users/<int:user_id>/roles', methods=['POST'])
@role_required('admin')
def admin_assign_user_roles(user_id):
    user = User.query.get(user_id)
    if not user:
        abort(404, description="User not found")
    
    data = request.get_json()
    role_names = data.get('role_names', [])
    
    if not isinstance(role_names, list):
        return jsonify(message="'role_names' must be a list"), 400
    
    user.roles = [] # Clear existing roles
    for role_name in role_names:
        role = Role.query.filter_by(name=role_name).first()
        if role:
            user.roles.append(role)
        else:
            return jsonify(message=f"Role '{role_name}' not found"), 404
            
    db.session.commit()
    return jsonify(message="User roles updated successfully", roles=[r.name for r in user.roles]), 200

@app.route('/api/admin/roles', methods=['GET'])
@role_required('admin')
def admin_get_all_roles():
    roles = Role.query.all()
    output = [{'id': role.id, 'name': role.name, 'description': role.description} for role in roles]
    return jsonify(roles=output), 200

# B. Subject Management

@app.route('/api/admin/subjects', methods=['POST'])
@role_required('admin')
def admin_create_subject():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')

    if not name:
        return jsonify(message="Subject name is required"), 400
    
    existing_subject = Subject.query.filter_by(name=name).first()
    if existing_subject:
        return jsonify(message="Subject with this name already exists"), 409

    new_subject = Subject(name=name, description=description)
    db.session.add(new_subject)
    db.session.commit()
    return jsonify(message="Subject created successfully", subject={'id': new_subject.id, 'name': new_subject.name}), 201

@app.route('/api/admin/subjects', methods=['GET'])
@role_required('admin')
def admin_get_all_subjects():
    subjects = Subject.query.all()
    output = [{'id': s.id, 'name': s.name, 'description': s.description} for s in subjects]
    return jsonify(subjects=output), 200

@app.route('/api/admin/subjects/<int:subject_id>', methods=['GET'])
@role_required('admin')
def admin_get_subject(subject_id):
    subject = Subject.query.get(subject_id)
    if not subject:
        abort(404, description="Subject not found")
    
    return jsonify(subject={'id': subject.id, 'name': subject.name, 'description': subject.description}), 200

@app.route('/api/admin/subjects/<int:subject_id>', methods=['PUT'])
@role_required('admin')
def admin_update_subject(subject_id):
    subject = Subject.query.get(subject_id)
    if not subject:
        abort(404, description="Subject not found")
    
    data = request.get_json()
    if 'name' in data:
        subject.name = data['name']
    if 'description' in data:
        subject.description = data['description']
    
    db.session.commit()
    return jsonify(message="Subject updated successfully"), 200

@app.route('/api/admin/subjects/<int:subject_id>', methods=['DELETE'])
@role_required('admin')
def admin_delete_subject(subject_id):
    subject = Subject.query.get(subject_id)
    if not subject:
        abort(404, description="Subject not found")
    
    # Check for dependent chapters/quizzes before deleting
    if subject.chapters:
        return jsonify(message="Cannot delete subject with associated chapters. Delete chapters first."), 409

    db.session.delete(subject)
    db.session.commit()
    return jsonify(message="Subject deleted successfully"), 200

# C. Chapter Management

@app.route('/api/admin/subjects/<int:subject_id>/chapters', methods=['POST'])
@role_required('admin')
def admin_create_chapter(subject_id):
    subject = Subject.query.get(subject_id)
    if not subject:
        abort(404, description="Subject not found")

    data = request.get_json()
    name = data.get('name')
    description = data.get('description')

    if not name:
        return jsonify(message="Chapter name is required"), 400
    
    existing_chapter = Chapter.query.filter_by(subject_id=subject_id, name=name).first()
    if existing_chapter:
        return jsonify(message="Chapter with this name already exists in this subject"), 409

    new_chapter = Chapter(subject_id=subject_id, name=name, description=description)
    db.session.add(new_chapter)
    db.session.commit()
    return jsonify(message="Chapter created successfully", chapter={'id': new_chapter.id, 'name': new_chapter.name}), 201

@app.route('/api/admin/subjects/<int:subject_id>/chapters', methods=['GET'])
@role_required('admin')
def admin_get_chapters_by_subject(subject_id):
    subject = Subject.query.get(subject_id)
    if not subject:
        abort(404, description="Subject not found")
    
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    output = [{'id': c.id, 'name': c.name, 'description': c.description, 'subject_id': c.subject_id} for c in chapters]
    return jsonify(chapters=output), 200

@app.route('/api/admin/chapters/<int:chapter_id>', methods=['GET'])
@role_required('admin')
def admin_get_chapter(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if not chapter:
        abort(404, description="Chapter not found")
    
    return jsonify(chapter={'id': chapter.id, 'name': chapter.name, 'description': chapter.description, 'subject_id': chapter.subject_id}), 200

@app.route('/api/admin/chapters/<int:chapter_id>', methods=['PUT'])
@role_required('admin')
def admin_update_chapter(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if not chapter:
        abort(404, description="Chapter not found")
    
    data = request.get_json()
    if 'name' in data:
        chapter.name = data['name']
    if 'description' in data:
        chapter.description = data['description']
    
    db.session.commit()
    return jsonify(message="Chapter updated successfully"), 200

@app.route('/api/admin/chapters/<int:chapter_id>', methods=['DELETE'])
@role_required('admin')
def admin_delete_chapter(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if not chapter:
        abort(404, description="Chapter not found")
    
    # Check for dependent quizzes before deleting
    if chapter.quizzes:
        return jsonify(message="Cannot delete chapter with associated quizzes. Delete quizzes first."), 409

    db.session.delete(chapter)
    db.session.commit()
    return jsonify(message="Chapter deleted successfully"), 200

# D. Quiz Management

@app.route('/api/admin/chapters/<int:chapter_id>/quizzes', methods=['POST'])
@role_required('admin')
def admin_create_quiz(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if not chapter:
        abort(404, description="Chapter not found")
    
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    time_duration = data.get('time_duration')
    remarks = data.get('remarks')
    is_published = data.get('is_published', False) # Default to False if not provided

    if not title or not time_duration:
        return jsonify(message="Quiz title and time duration are required"), 400
    
    try:
        time_duration = int(time_duration)
        if time_duration <= 0:
            raise ValueError
    except ValueError:
        return jsonify(message="Time duration must be a positive integer"), 400

    new_quiz = Quiz(
        chapter_id=chapter_id,
        title=title,
        description=description,
        time_duration=time_duration,
        remarks=remarks,
        is_published=is_published
    )
    db.session.add(new_quiz)
    db.session.commit()
    return jsonify(message="Quiz created successfully", quiz={'id': new_quiz.id, 'title': new_quiz.title}), 201

@app.route('/api/admin/chapters/<int:chapter_id>/quizzes', methods=['GET'])
@role_required('admin')
def admin_get_quizzes_by_chapter(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if not chapter:
        abort(404, description="Chapter not found")
    
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    output = []
    for quiz in quizzes:
        output.append({
            'id': quiz.id,
            'chapter_id': quiz.chapter_id,
            'title': quiz.title,
            'description': quiz.description,
            'date_of_quiz': quiz.date_of_quiz.isoformat(),
            'time_duration': quiz.time_duration,
            'remarks': quiz.remarks,
            'is_published': quiz.is_published
        })
    return jsonify(quizzes=output), 200

@app.route('/api/admin/quizzes', methods=['GET'])
@role_required('admin')
def admin_get_all_quizzes():
    # Allow filtering by subject_id, chapter_id, and published status
    subject_id = request.args.get('subject_id', type=int)
    chapter_id = request.args.get('chapter_id', type=int)
    is_published = request.args.get('published')

    query = db.session.query(Quiz)

    if subject_id:
        query = query.join(Chapter).filter(Chapter.subject_id == subject_id)
    if chapter_id:
        query = query.filter(Quiz.chapter_id == chapter_id)
    if is_published is not None:
        query = query.filter(Quiz.is_published == (is_published.lower() == 'true'))

    quizzes = query.all()
    output = []
    for quiz in quizzes:
        output.append({
            'id': quiz.id,
            'chapter_id': quiz.chapter_id,
            'title': quiz.title,
            'description': quiz.description,
            'date_of_quiz': quiz.date_of_quiz.isoformat(),
            'time_duration': quiz.time_duration,
            'remarks': quiz.remarks,
            'is_published': quiz.is_published,
            'subject_name': quiz.chapter.subject.name if quiz.chapter and quiz.chapter.subject else None,
            'chapter_name': quiz.chapter.name if quiz.chapter else None
        })
    return jsonify(quizzes=output), 200

@app.route('/api/admin/quizzes/<int:quiz_id>', methods=['GET'])
@role_required('admin')
def admin_get_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        abort(404, description="Quiz not found")
    
    questions_data = []
    for question in quiz.questions:
        q_data = {
            'id': question.id,
            'question_statement': question.question_statement,
            'question_type': question.question_type.value,
            'points': question.points,
            'correct_answer': question.correct_answer # Admin can see correct answer
        }
        if question.question_type == QuestionType.MCQ:
            q_data['options'] = [question.option1, question.option2, question.option3, question.option4]
            q_data['options'] = [opt for opt in q_data['options'] if opt is not None] # Filter out None options
        questions_data.append(q_data)

    quiz_data = {
        'id': quiz.id,
        'chapter_id': quiz.chapter_id,
        'title': quiz.title,
        'description': quiz.description,
        'date_of_quiz': quiz.date_of_quiz.isoformat(),
        'time_duration': quiz.time_duration,
        'remarks': quiz.remarks,
        'is_published': quiz.is_published,
        'questions': questions_data
    }
    return jsonify(quiz=quiz_data), 200

@app.route('/api/admin/quizzes/<int:quiz_id>', methods=['PUT'])
@role_required('admin')
def admin_update_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        abort(404, description="Quiz not found")
    
    data = request.get_json()
    if 'title' in data:
        quiz.title = data['title']
    if 'description' in data:
        quiz.description = data['description']
    if 'time_duration' in data:
        try:
            quiz.time_duration = int(data['time_duration'])
            if quiz.time_duration <= 0:
                raise ValueError
        except ValueError:
            return jsonify(message="Time duration must be a positive integer"), 400
    if 'remarks' in data:
        quiz.remarks = data['remarks']
    if 'is_published' in data:
        quiz.is_published = bool(data['is_published'])
    
    db.session.commit()
    return jsonify(message="Quiz updated successfully"), 200

@app.route('/api/admin/quizzes/<int:quiz_id>/publish', methods=['PATCH'])
@role_required('admin')
def admin_publish_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        abort(404, description="Quiz not found")
    
    data = request.get_json()
    is_published = data.get('is_published')
    
    if is_published is None or not isinstance(is_published, bool):
        return jsonify(message="'is_published' (boolean) is required"), 400
        
    quiz.is_published = is_published
    db.session.commit()
    # Send quiz reminder if quiz is being published (not unpublished)
    if is_published:
        quiz_remainder.delay("admin@mail.com")  # Send to admin email for now
    return jsonify(message=f"Quiz {'published' if is_published else 'unpublished'} successfully", is_published=quiz.is_published), 200

@app.route('/api/admin/quizzes/<int:quiz_id>', methods=['DELETE'])
@role_required('admin')
def admin_delete_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        abort(404, description="Quiz not found")
    
    # Delete associated questions, user answers, and scores
    for question in quiz.questions:
        for user_answer in question.user_answers:
            db.session.delete(user_answer)
        db.session.delete(question)
    
    for score in quiz.scores:
        for user_answer in score.user_answers:
            db.session.delete(user_answer)
        db.session.delete(score)

    db.session.delete(quiz)
    db.session.commit()
    return jsonify(message="Quiz deleted successfully"), 200

# E. Question Management

@app.route('/api/admin/quizzes/<int:quiz_id>/questions', methods=['POST'])
@role_required('admin')
def admin_create_question(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        abort(404, description="Quiz not found")
    
    data = request.get_json()
    question_statement = data.get('question_statement')
    question_type_str = data.get('question_type')
    points = data.get('points', 1)
    correct_answer = data.get('correct_answer')
    
    if not question_statement or not question_type_str or not correct_answer:
        return jsonify(message="Question statement, type, and correct answer are required"), 400
    
    try:
        question_type = QuestionType[question_type_str.upper()]
    except KeyError:
        return jsonify(message=f"Invalid question type. Must be one of: {[q.name for q in QuestionType]}"), 400

    new_question = Question(
        quiz_id=quiz_id,
        question_statement=question_statement,
        question_type=question_type,
        points=points,
        correct_answer=correct_answer
    )

    if question_type == QuestionType.MCQ:
        new_question.option1 = data.get('option1')
        new_question.option2 = data.get('option2')
        new_question.option3 = data.get('option3')
        new_question.option4 = data.get('option4')
        
        if not all([new_question.option1, new_question.option2, new_question.option3, new_question.option4]):
            return jsonify(message="MCQ questions require all 4 options"), 400
        if correct_answer not in [new_question.option1, new_question.option2, new_question.option3, new_question.option4]:
            return jsonify(message="Correct answer for MCQ must be one of the provided options"), 400
    
    db.session.add(new_question)
    db.session.commit()
    # Send quiz reminder if quiz is being published (not unpublished)
    if is_published:
        quiz_remainder.delay("admin@mail.com")  # Send to admin email for now
    return jsonify(message="Question created successfully", question={'id': new_question.id, 'statement': new_question.question_statement}), 201

@app.route('/api/admin/quizzes/<int:quiz_id>/questions', methods=['GET'])
@role_required('admin')
def admin_get_questions_by_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        abort(404, description="Quiz not found")
    
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    output = []
    for question in questions:
        q_data = {
            'id': question.id,
            'question_statement': question.question_statement,
            'question_type': question.question_type.value,
            'points': question.points,
            'correct_answer': question.correct_answer
        }
        if question.question_type == QuestionType.MCQ:
            q_data['options'] = [question.option1, question.option2, question.option3, question.option4]
            q_data['options'] = [opt for opt in q_data['options'] if opt is not None]
        output.append(q_data)
    return jsonify(questions=output), 200

@app.route('/api/admin/questions/<int:question_id>', methods=['GET'])
@role_required('admin')
def admin_get_question(question_id):
    question = Question.query.get(question_id)
    if not question:
        abort(404, description="Question not found")
    
    q_data = {
        'id': question.id,
        'quiz_id': question.quiz_id,
        'question_statement': question.question_statement,
        'question_type': question.question_type.value,
        'points': question.points,
        'correct_answer': question.correct_answer
    }
    if question.question_type == QuestionType.MCQ:
        q_data['options'] = [question.option1, question.option2, question.option3, question.option4]
        q_data['options'] = [opt for opt in q_data['options'] if opt is not None]
    return jsonify(question=q_data), 200

@app.route('/api/admin/questions/<int:question_id>', methods=['PUT'])
@role_required('admin')
def admin_update_question(question_id):
    question = Question.query.get(question_id)
    if not question:
        abort(404, description="Question not found")
    
    data = request.get_json()
    if 'question_statement' in data:
        question.question_statement = data['question_statement']
    if 'question_type' in data:
        try:
            question.question_type = QuestionType[data['question_type'].upper()]
        except KeyError:
            return jsonify(message=f"Invalid question type. Must be one of: {[q.name for q in QuestionType]}"), 400
    if 'points' in data:
        question.points = data['points']
    if 'correct_answer' in data:
        question.correct_answer = data['correct_answer']
    
    if question.question_type == QuestionType.MCQ:
        question.option1 = data.get('option1', question.option1)
        question.option2 = data.get('option2', question.option2)
        question.option3 = data.get('option3', question.option3)
        question.option4 = data.get('option4', question.option4)
        
        if not all([question.option1, question.option2, question.option3, question.option4]):
            return jsonify(message="MCQ questions require all 4 options"), 400
        if question.correct_answer not in [question.option1, question.option2, question.option3, question.option4]:
            return jsonify(message="Correct answer for MCQ must be one of the provided options"), 400

    db.session.commit()
    return jsonify(message="Question updated successfully"), 200

@app.route('/api/admin/questions/<int:question_id>', methods=['DELETE'])
@role_required('admin')
def admin_delete_question(question_id):
    question = Question.query.get(question_id)
    if not question:
        abort(404, description="Question not found")
    
    # Delete associated user answers
    for user_answer in question.user_answers:
        db.session.delete(user_answer)

    db.session.delete(question)
    db.session.commit()
    return jsonify(message="Question deleted successfully"), 200

# F. Score/Result Management (Admin View)

@app.route('/api/admin/scores', methods=['GET'])
@role_required('admin')
def admin_get_all_scores():
    user_id = request.args.get('user_id', type=int)
    quiz_id = request.args.get('quiz_id', type=int)
    subject_id = request.args.get('subject_id', type=int)

    query = db.session.query(Score)

    if user_id:
        query = query.filter(Score.user_id == user_id)
    if quiz_id:
        query = query.filter(Score.quiz_id == quiz_id)
    if subject_id:
        query = query.join(Quiz).join(Chapter).filter(Chapter.subject_id == subject_id)

    scores = query.all()
    output = []
    for score in scores:
        output.append({
            'id': score.id,
            'quiz_id': score.quiz_id,
            'user_id': score.user_id,
            'user_email': score.user.email if score.user else None,
            'quiz_title': score.quiz.title if score.quiz else None,
            'time_stamp_of_attempt': score.time_stamp_of_attempt.isoformat(),
            'total_scored': score.total_scored,
            'total_possible': score.total_possible,
            'completion_time': score.completion_time
        })
    return jsonify(scores=output), 200

@app.route('/api/admin/scores/<int:score_id>', methods=['GET'])
@role_required('admin')
def admin_get_score_details(score_id):
    score = Score.query.get(score_id)
    if not score:
        abort(404, description="Score not found")
    
    user_answers_data = []
    for ua in score.user_answers:
        user_answers_data.append({
            'id': ua.id,
            'question_id': ua.question_id,
            'question_statement': ua.question.question_statement if ua.question else None,
            'user_answer': ua.user_answer,
            'is_correct': ua.is_correct,
            'points_earned': ua.points_earned,
            'correct_answer': ua.question.correct_answer if ua.question else None # Admin can see correct answer
        })

    score_data = {
        'id': score.id,
        'quiz_id': score.quiz_id,
        'user_id': score.user_id,
        'user_email': score.user.email if score.user else None,
        'quiz_title': score.quiz.title if score.quiz else None,
        'time_stamp_of_attempt': score.time_stamp_of_attempt.isoformat(),
        'total_scored': score.total_scored,
        'total_possible': score.total_possible,
        'completion_time': score.completion_time,
        'user_answers': user_answers_data
    }
    return jsonify(score=score_data), 200

@app.route('/api/admin/quizzes/<int:quiz_id>/scores', methods=['GET'])
@role_required('admin')
def admin_get_scores_for_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        abort(404, description="Quiz not found")
    
    scores = Score.query.filter_by(quiz_id=quiz_id).all()
    output = []
    for score in scores:
        output.append({
            'id': score.id,
            'user_id': score.user_id,
            'user_email': score.user.email if score.user else None,
            'time_stamp_of_attempt': score.time_stamp_of_attempt.isoformat(),
            'total_scored': score.total_scored,
            'total_possible': score.total_possible,
            'completion_time': score.completion_time
        })
    return jsonify(scores=output), 200

@app.route('/api/admin/users/<int:user_id>/scores', methods=['GET'])
@role_required('admin')
def admin_get_scores_for_user(user_id):
    user = User.query.get(user_id)
    if not user:
        abort(404, description="User not found")
    
    scores = Score.query.filter_by(user_id=user_id).all()
    output = []
    for score in scores:
        output.append({
            'id': score.id,
            'quiz_id': score.quiz_id,
            'quiz_title': score.quiz.title if score.quiz else None,
            'time_stamp_of_attempt': score.time_stamp_of_attempt.isoformat(),
            'total_scored': score.total_scored,
            'total_possible': score.total_possible,
            'completion_time': score.completion_time
        })
    return jsonify(scores=output), 200

@app.route('/api/admin/analytics/quiz/<int:quiz_id>', methods=['GET'])
@role_required('admin')
def admin_quiz_analytics(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        abort(404, description="Quiz not found")
    
    scores = Score.query.filter_by(quiz_id=quiz_id).all()
    
    total_attempts = len(scores)
    if total_attempts == 0:
        return jsonify(message="No attempts for this quiz yet."), 200
    
    total_scored_sum = sum(s.total_scored for s in scores)
    total_possible_sum = sum(s.total_possible for s in scores)
    
    average_score = (total_scored_sum / total_possible_sum) * 100 if total_possible_sum > 0 else 0
    
    # Example: Analyze question performance
    question_performance = {}
    for question in quiz.questions:
        correct_count = 0
        total_answers = 0
        for user_answer in question.user_answers:
            if user_answer.is_correct:
                correct_count += 1
            total_answers += 1
        
        accuracy = (correct_count / total_answers) * 100 if total_answers > 0 else 0
        question_performance[question.id] = {
            'statement': question.question_statement,
            'accuracy': round(accuracy, 2),
            'total_answers': total_answers,
            'correct_answers': correct_count
        }

    return jsonify(
        quiz_id=quiz_id,
        quiz_title=quiz.title,
        total_attempts=total_attempts,
        average_score_percentage=round(average_score, 2),
        question_performance=question_performance
    ), 200

@app.route('/api/admin/analytics/subject/<int:subject_id>', methods=['GET'])
@role_required('admin')
def admin_subject_analytics(subject_id):
    subject = Subject.query.get(subject_id)
    if not subject:
        abort(404, description="Subject not found")

    # Get all quizzes related to this subject
    quizzes_in_subject = db.session.query(Quiz).join(Chapter).filter(Chapter.subject_id == subject_id).all()
    
    total_subject_scores = 0
    total_subject_possible = 0
    quiz_summaries = []

    for quiz in quizzes_in_subject:
        scores = Score.query.filter_by(quiz_id=quiz.id).all()
        quiz_total_scored = sum(s.total_scored for s in scores)
        quiz_total_possible = sum(s.total_possible for s in scores)
        
        total_subject_scores += quiz_total_scored
        total_subject_possible += quiz_total_possible
        
        quiz_summaries.append({
            'quiz_id': quiz.id,
            'quiz_title': quiz.title,
            'total_attempts': len(scores),
            'average_score_percentage': (quiz_total_scored / quiz_total_possible * 100) if quiz_total_possible > 0 else 0
        })

    average_subject_score = (total_subject_scores / total_subject_possible) * 100 if total_subject_possible > 0 else 0

    return jsonify(
        subject_id=subject_id,
        subject_name=subject.name,
        total_quizzes=len(quizzes_in_subject),
        overall_average_score_percentage=round(average_subject_score, 2),
        quiz_summaries=quiz_summaries
    ), 200

@app.route('/api/admin/analytics/user/<int:user_id>', methods=['GET'])
@role_required('admin')
def admin_user_analytics(user_id):
    user = User.query.get(user_id)
    if not user:
        abort(404, description="User not found")
    
    scores = Score.query.filter_by(user_id=user_id).all()
    
    total_quizzes_attempted = len(scores)
    if total_quizzes_attempted == 0:
        return jsonify(message="User has not attempted any quizzes yet."), 200
    
    total_scored_sum = sum(s.total_scored for s in scores)
    total_possible_sum = sum(s.total_possible for s in scores)
    
    overall_average_score = (total_scored_sum / total_possible_sum) * 100 if total_possible_sum > 0 else 0

    # Group scores by subject/chapter for more detailed analytics
    performance_by_subject = {}
    for score in scores:
        if score.quiz and score.quiz.chapter and score.quiz.chapter.subject:
            subject_name = score.quiz.chapter.subject.name
            if subject_name not in performance_by_subject:
                performance_by_subject[subject_name] = {'total_scored': 0, 'total_possible': 0, 'attempts': 0}
            
            performance_by_subject[subject_name]['total_scored'] += score.total_scored
            performance_by_subject[subject_name]['total_possible'] += score.total_possible
            performance_by_subject[subject_name]['attempts'] += 1
    
    for subject_name, data in performance_by_subject.items():
        data['average_score_percentage'] = (data['total_scored'] / data['total_possible'] * 100) if data['total_possible'] > 0 else 0
        data['average_score_percentage'] = round(data['average_score_percentage'], 2)

    return jsonify(
        user_id=user_id,
        user_email=user.email,
        total_quizzes_attempted=total_quizzes_attempted,
        overall_average_score_percentage=round(overall_average_score, 2),
        performance_by_subject=performance_by_subject
    ), 200

# III. User Endpoints

# A. User Profile (already covered by /api/auth/me, but keeping a dedicated one for student profile updates)

@app.route('/api/users/me/profile', methods=['PUT'])
@jwt_required()
def user_update_profile():
    current_user_email = get_jwt_identity()
    current_user = User.query.filter_by(email=current_user_email).first()
    
    if not current_user:
        abort(404, description="User not found")
    
    if not current_user.student_profile:
        return jsonify(message="Student profile not found for this user."), 404

    data = request.get_json()
    if 'name' in data:
        current_user.student_profile.name = data['name']
    if 'dob' in data:
        try:
            if '/' in data['dob']:
                current_user.student_profile.dob = datetime.strptime(data['dob'], '%d/%m/%Y').date()
            elif '-' in data['dob']:
                current_user.student_profile.dob = datetime.strptime(data['dob'], '%Y-%m-%d').date()
            else:
                return jsonify(message="Invalid date format for DOB. Use DD/MM/YYYY or YYYY-MM-DD"), 400
        except ValueError:
            return jsonify(message="Invalid date format for DOB. Use DD/MM/YYYY or YYYY-MM-DD"), 400
    if 'qualification' in data:
        current_user.student_profile.qualification = data['qualification']
    
    db.session.commit()
    return jsonify(message="Student profile updated successfully", 
                   profile={
                       'name': current_user.student_profile.name,
                       'dob': current_user.student_profile.dob.isoformat(),
                       'qualification': current_user.student_profile.qualification
                   }), 200

# B. Quiz Browsing & Taking

@app.route('/api/subjects', methods=['GET'])
@jwt_required()
def get_all_subjects():
    subjects = Subject.query.all()
    output = [{'id': s.id, 'name': s.name, 'description': s.description} for s in subjects]
    return jsonify(subjects=output), 200

@app.route('/api/subjects/<int:subject_id>/chapters', methods=['GET'])
@jwt_required()
def get_chapters_for_subject(subject_id):
    subject = Subject.query.get(subject_id)
    if not subject:
        abort(404, description="Subject not found")
    
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    output = [{'id': c.id, 'name': c.name, 'description': c.description, 'subject_id': c.subject_id} for c in chapters]
    return jsonify(chapters=output), 200

@app.route('/api/chapters/<int:chapter_id>/quizzes', methods=['GET'])
@jwt_required()
def get_published_quizzes_by_chapter(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if not chapter:
        abort(404, description="Chapter not found")
    
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id, is_published=True).all()
    output = []
    for quiz in quizzes:
        output.append({
            'id': quiz.id,
            'title': quiz.title,
            'description': quiz.description,
            'time_duration': quiz.time_duration,
            'date_of_quiz': quiz.date_of_quiz.isoformat()
        })
    return jsonify(quizzes=output), 200

@app.route('/api/quizzes', methods=['GET'])
@jwt_required()
def get_all_published_quizzes():
    quizzes = Quiz.query.filter_by(is_published=True).all()
    output = []
    for quiz in quizzes:
        quiz_data = {
            'id': quiz.id,
            'title': quiz.title,
            'description': quiz.description,
            'time_duration': quiz.time_duration,
            'date_of_quiz': quiz.date_of_quiz.isoformat(),
            'chapter_name': quiz.chapter.name if quiz.chapter else None,
            'subject_name': quiz.chapter.subject.name if quiz.chapter and quiz.chapter.subject else None,
            'is_published': quiz.is_published
        }
        output.append(quiz_data)
    return jsonify(quizzes=output), 200

@app.route('/api/quizzes/<int:quiz_id>', methods=['GET'])
@jwt_required()
def get_quiz_details_for_user(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz or not quiz.is_published:
        abort(404, description="Quiz not found or not published")
    
    # Return only necessary details for a user before starting the quiz
    quiz_data = {
        'id': quiz.id,
        'title': quiz.title,
        'description': quiz.description,
        'time_duration': quiz.time_duration,
        'date_of_quiz': quiz.date_of_quiz.isoformat(),
        'chapter_name': quiz.chapter.name if quiz.chapter else None,
        'subject_name': quiz.chapter.subject.name if quiz.chapter and quiz.chapter.subject else None
    }
    return jsonify(quiz=quiz_data), 200

@app.route('/api/quizzes/<int:quiz_id>/start', methods=['POST'])
@jwt_required()
def start_quiz(quiz_id):
    current_user_email = get_jwt_identity()
    current_user = User.query.filter_by(email=current_user_email).first()
    
    if not current_user:
        abort(404, description="User not found")

    quiz = Quiz.query.get(quiz_id)
    if not quiz or not quiz.is_published:
        abort(404, description="Quiz not found or not published")
    
    # Create a new Score entry for this attempt
    new_score = Score(
        quiz_id=quiz.id,
        user_id=current_user.id,
        time_stamp_of_attempt=datetime.utcnow(),
        total_scored=0, # Will be updated on submission
        total_possible=sum(q.points for q in quiz.questions),
        completion_time=0 # Will be updated on submission
    )
    db.session.add(new_score)
    db.session.commit() # Commit to get score_id

    # Prepare questions for the user (shuffle, hide correct answers)
    questions_for_user = []
    import random
    shuffled_questions = random.sample(quiz.questions, len(quiz.questions)) # Shuffle questions
    
    for question in shuffled_questions:
        q_data = {
            'id': question.id,
            'question_statement': question.question_statement,
            'question_type': question.question_type.value,
            'points': question.points
        }
        if question.question_type == QuestionType.MCQ:
            options = [question.option1, question.option2, question.option3, question.option4]
            options = [opt for opt in options if opt is not None]
            random.shuffle(options) # Shuffle options
            q_data['options'] = options
        questions_for_user.append(q_data)

    return jsonify(
        message="Quiz started",
        score_id=new_score.id,
        quiz_id=quiz.id,
        quiz_title=quiz.title,
        time_duration=quiz.time_duration,
        questions=questions_for_user
    ), 200

@app.route('/api/quiz-sessions/<int:score_id>', methods=['GET'])
@jwt_required()
def get_quiz_session(score_id):
    current_user_email = get_jwt_identity()
    current_user = User.query.filter_by(email=current_user_email).first()
    
    if not current_user:
        abort(404, description="User not found")

    # Get the score record to verify ownership and get quiz info
    score = Score.query.filter_by(id=score_id, user_id=current_user.id).first()
    if not score:
        abort(404, description="Quiz session not found or does not belong to current user")
    
    quiz = score.quiz
    if not quiz:
        abort(404, description="Quiz not found")
    
    # Prepare questions for the user (same as start_quiz but without creating new score)
    questions_for_user = []
    import random
    shuffled_questions = list(quiz.questions)  # Convert to list for shuffling
    random.shuffle(shuffled_questions) # Shuffle questions
    
    for question in shuffled_questions:
        q_data = {
            'id': question.id,
            'question_statement': question.question_statement,
            'question_type': question.question_type.value,
            'points': question.points
        }
        if question.question_type == QuestionType.MCQ:
            options = [question.option1, question.option2, question.option3, question.option4]
            options = [opt for opt in options if opt is not None]
            random.shuffle(options) # Shuffle options
            q_data['options'] = options
        questions_for_user.append(q_data)

    return jsonify(
        score_id=score.id,
        quiz_id=quiz.id,
        quiz_title=quiz.title,
        time_duration=quiz.time_duration,
        subject_name=quiz.chapter.subject.name if quiz.chapter and quiz.chapter.subject else None,
        chapter_name=quiz.chapter.name if quiz.chapter else None,
        questions=questions_for_user
    ), 200

@app.route('/api/quizzes/<int:quiz_id>/submit', methods=['POST'])
@jwt_required()
def submit_quiz(quiz_id):
    current_user_email = get_jwt_identity()
    current_user = User.query.filter_by(email=current_user_email).first()
    
    if not current_user:
        abort(404, description="User not found")

    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        abort(404, description="Quiz not found")
    
    data = request.get_json()
    user_answers_data = data.get('answers', [])
    score_id = data.get('score_id')
    completion_time = data.get('completion_time', 0) # Time taken in seconds

    if not score_id:
        return jsonify(message="Score ID is required to submit answers"), 400

    score_record = Score.query.filter_by(id=score_id, quiz_id=quiz_id, user_id=current_user.id).first()
    if not score_record:
        return jsonify(message="Score record not found or does not belong to current user/quiz"), 404

    total_scored = 0
    total_possible = sum(q.points for q in quiz.questions)
    
    for answer_data in user_answers_data:
        question_id = answer_data.get('question_id')
        user_answer_text = answer_data.get('user_answer')
        
        question = Question.query.get(question_id)
        if not question or question.quiz_id != quiz.id:
            # Skip invalid questions or questions not belonging to this quiz
            continue 
        
        is_correct = False
        points_earned = 0

        # Compare user answer with correct answer based on question type
        if question.question_type == QuestionType.MCQ or question.question_type == QuestionType.TRUE_FALSE:
            if user_answer_text and user_answer_text.strip().lower() == question.correct_answer.strip().lower():
                is_correct = True
        elif question.question_type == QuestionType.SHORT_ANSWER or question.question_type == QuestionType.FILL_BLANK:
            # For short answer/fill blank, a simple string comparison
            if user_answer_text and user_answer_text.strip().lower() == question.correct_answer.strip().lower():
                is_correct = True
        
        if is_correct:
            points_earned = question.points
            total_scored += points_earned
        
        # Create UserAnswer record
        new_user_answer = UserAnswer(
            score_id=score_record.id,
            question_id=question.id,
            user_id=current_user.id,
            user_answer=user_answer_text if user_answer_text is not None else "",
            is_correct=is_correct,
            points_earned=points_earned
        )
        db.session.add(new_user_answer)
    
    score_record.total_scored = total_scored
    score_record.total_possible = total_possible
    score_record.completion_time = completion_time
    db.session.commit()

    return jsonify(
        message="Quiz submitted successfully",
        score_id=score_record.id,
        total_scored=score_record.total_scored,
        total_possible=score_record.total_possible,
        completion_time=score_record.completion_time
    ), 200

# C. Score & Result Viewing (User View)

@app.route('/api/users/me/scores', methods=['GET'])
@jwt_required()
def get_my_scores():
    current_user_email = get_jwt_identity()
    current_user = User.query.filter_by(email=current_user_email).first()
    
    if not current_user:
        abort(404, description="User not found")

    subject_id = request.args.get('subject_id', type=int)
    quiz_id = request.args.get('quiz_id', type=int)

    query = Score.query.filter_by(user_id=current_user.id)

    if quiz_id:
        query = query.filter(Score.quiz_id == quiz_id)
    if subject_id:
        query = query.join(Quiz).join(Chapter).filter(Chapter.subject_id == subject_id)

    scores = query.all()
    output = []
    for score in scores:
        output.append({
            'id': score.id,
            'quiz_id': score.quiz_id,
            'quiz_title': score.quiz.title if score.quiz else None,
            'time_stamp_of_attempt': score.time_stamp_of_attempt.isoformat(),
            'total_scored': score.total_scored,
            'total_possible': score.total_possible,
            'completion_time': score.completion_time,
            'subject_name': score.quiz.chapter.subject.name if score.quiz and score.quiz.chapter and score.quiz.chapter.subject else None,
            'chapter_name': score.quiz.chapter.name if score.quiz and score.quiz.chapter else None
        })
    return jsonify(scores=output), 200

@app.route('/api/scores/<int:score_id>', methods=['GET'])
@jwt_required()
def get_my_score_details(score_id):
    current_user_email = get_jwt_identity()
    current_user = User.query.filter_by(email=current_user_email).first()
    
    if not current_user:
        abort(404, description="User not found")

    score = Score.query.filter_by(id=score_id, user_id=current_user.id).first()
    if not score:
        abort(404, description="Score not found or does not belong to current user")
    
    user_answers_data = []
    for ua in score.user_answers:
        user_answers_data.append({
            'id': ua.id,
            'question_id': ua.question_id,
            'question_statement': ua.question.question_statement if ua.question else None,
            'user_answer': ua.user_answer,
            'is_correct': ua.is_correct,
            'points_earned': ua.points_earned,
            'correct_answer': ua.question.correct_answer if ua.question else None # User can see correct answer on review
        })

    score_data = {
        'id': score.id,
        'quiz_id': score.quiz_id,
        'quiz_title': score.quiz.title if score.quiz else None,
        'time_stamp_of_attempt': score.time_stamp_of_attempt.isoformat(),
        'total_scored': score.total_scored,
        'total_possible': score.total_possible,
        'completion_time': score.completion_time,
        'subject_name': score.quiz.chapter.subject.name if score.quiz and score.quiz.chapter and score.quiz.chapter.subject else None,
        'chapter_name': score.quiz.chapter.name if score.quiz and score.quiz.chapter else None,
        'user_answers': user_answers_data
    }
    return jsonify(score=score_data), 200

@app.route('/api/users/me/analytics/performance', methods=['GET'])
@jwt_required()
def get_my_performance_analytics():
    current_user_email = get_jwt_identity()
    current_user = User.query.filter_by(email=current_user_email).first()
    
    if not current_user:
        abort(404, description="User not found")
    
    scores = Score.query.filter_by(user_id=current_user.id).all()
    
    total_quizzes_attempted = len(scores)
    if total_quizzes_attempted == 0:
        return jsonify(message="You have not attempted any quizzes yet."), 200
    
    total_scored_sum = sum(s.total_scored for s in scores)
    total_possible_sum = sum(s.total_possible for s in scores)
    
    overall_average_score = (total_scored_sum / total_possible_sum) * 100 if total_possible_sum > 0 else 0

    performance_by_subject = {}
    for score in scores:
        if score.quiz and score.quiz.chapter and score.quiz.chapter.subject:
            subject_name = score.quiz.chapter.subject.name
            if subject_name not in performance_by_subject:
                performance_by_subject[subject_name] = {'total_scored': 0, 'total_possible': 0, 'attempts': 0}
            
            performance_by_subject[subject_name]['total_scored'] += score.total_scored
            performance_by_subject[subject_name]['total_possible'] += score.total_possible
            performance_by_subject[subject_name]['attempts'] += 1
    
    for subject_name, data in performance_by_subject.items():
        data['average_score_percentage'] = (data['total_scored'] / data['total_possible'] * 100) if data['total_possible'] > 0 else 0
        data['average_score_percentage'] = round(data['average_score_percentage'], 2)

    return jsonify(
        user_id=current_user.id,
        user_email=current_user.email,
        total_quizzes_attempted=total_quizzes_attempted,
        overall_average_score_percentage=round(overall_average_score, 2),
        performance_by_subject=performance_by_subject
    ), 200


@app.route('/api/export')    # manually triggers the job
def export_csv():
    result = download_csv_report.delay() # async object
    return jsonify({
        "id": result.id,
        "result": result.result
    })

@app.route('/api/csv_result/<id>') # just created to test the status of  result
def csv_result(id):
    result = AsyncResult(id)
    return send_from_directory('static', result.result) if result.successful() else jsonify({"status": "Processing"}), 200

