# QuizApp v2

A modern, full-stack quiz application platform built with Flask and Vue.js that enables educational institutions to create, manage, and conduct online assessments with comprehensive analytics and reporting capabilities.

## 🚀 Features

### For Administrators
- **User Management**: Complete CRUD operations for user accounts with role-based access control
- **Content Management**: Hierarchical organization with Subjects → Chapters → Quizzes → Questions
- **Quiz Creation**: Support for multiple question types (MCQ, True/False, Short Answer, Fill in the Blank)
- **Analytics Dashboard**: Comprehensive performance tracking and reporting
- **Data Export**: CSV export functionality for score data and analytics
- **Background Tasks**: Automated monthly reports and quiz notifications

### For Students
- **Interactive Quiz Taking**: Real-time quiz sessions with automatic scoring
- **Performance Analytics**: Detailed progress tracking and performance insights
- **Score History**: Complete history of quiz attempts and results
- **Responsive Interface**: Mobile-friendly design for accessibility

### System Features
- **JWT Authentication**: Secure token-based authentication system
- **Role-Based Access**: Admin and student roles with appropriate permissions
- **Background Processing**: Celery-powered asynchronous task processing
- **Email Notifications**: Automated monthly progress reports
- **Google Chat Integration**: Quiz reminders and notifications
- **Question Randomization**: Anti-cheating measures with shuffled questions and options

## 🛠️ Technology Stack

### Backend
- **Flask 3.1.1**: Core web framework
- **Flask-SQLAlchemy 3.1.1**: ORM for database operations
- **Flask-JWT-Extended 4.7.1**: JWT authentication
- **Flask-CORS 6.0.1**: Cross-origin resource sharing
- **Celery 5.5.3**: Asynchronous task processing
- **Redis 5.2.1**: Message broker and caching
- **SQLite**: Database (development)
- **Bcrypt 4.3.0**: Password hashing

### Frontend
- **Vue.js 3.5.17**: Progressive JavaScript framework
- **Vue Router 4.5.1**: Client-side routing
- **Vite 7.0.4**: Build tool and development server
- **Axios 1.11.0**: HTTP client

## 📋 Prerequisites

Before running this application, make sure you have the following installed:

- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn
- Redis server

## ⚡ Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/abhinv11/iitm_quizapp_v2.git
cd iitm_quizapp_v2
```

### 2. Backend Setup

#### Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### Database Setup
```bash
# Initialize the database
python app.py
```

#### Start Redis Server
```bash
# On Ubuntu/Debian
sudo systemctl start redis-server

# On macOS with Homebrew
brew services start redis

# On Windows or manual start
redis-server
```

#### Start Celery Worker (in a separate terminal)
```bash
cd backend
celery -A app.celery worker --loglevel=info
```

#### Start Celery Beat (for scheduled tasks, in another terminal)
```bash
cd backend
celery -A app.celery beat --loglevel=info
```

#### Start Flask Backend
```bash
cd backend
python app.py
```

The backend will be available at `http://localhost:5000`

### 3. Frontend Setup

#### Install Dependencies
```bash
cd Frontend
npm install
```

#### Start Development Server
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## 🏗️ Project Structure

```
iitm_quizapp_v2/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── requirements.txt       # Python dependencies
│   ├── application/
│   │   ├── config.py         # Configuration settings
│   │   ├── database.py       # Database initialization
│   │   ├── models.py         # SQLAlchemy models
│   │   ├── routes.py         # API endpoints
│   │   ├── security.py       # JWT configuration
│   │   ├── tasks.py          # Celery background tasks
│   │   ├── celery_init.py    # Celery initialization
│   │   ├── mail.py           # Email functionality
│   │   └── utils.py          # Utility functions
│   ├── instance/
│   │   └── quizappDb.sqlite3 # SQLite database
│   └── static/               # Static files and exports
├── Frontend/
│   ├── package.json          # Node.js dependencies
│   ├── vite.config.js        # Vite configuration
│   ├── index.html            # Main HTML template
│   └── src/
│       ├── App.vue           # Root Vue component
│       ├── main.js           # Application entry point
│       ├── routes.js         # Vue Router configuration
│       ├── assets/           # Static assets
│       └── components/       # Vue components
│           ├── AdminPage.vue
│           ├── LoginPage.vue
│           ├── QuizzesPage.vue
│           └── ...
├── endpoints.txt             # API documentation
├── project_report.txt        # Project report
├── requirements.txt          # Root dependencies
└── README.md                 # This file
```

## 🔧 Configuration

### Backend Configuration
The application uses environment-based configuration. Key settings in `backend/application/config.py`:

```python
class LocalDevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///quizappDb.sqlite3"
    JWT_SECRET_KEY = 'your_jwt_secret_key_here'
    SECURITY_PASSWORD_HASH = 'bcrypt'
```

### Database Schema
The application uses the following main entities:
- **Users**: Authentication and profile management
- **Roles**: Admin and student role definitions
- **Subjects**: Top-level academic categories
- **Chapters**: Subject subdivisions
- **Quizzes**: Assessment containers
- **Questions**: Individual quiz items
- **Scores**: Quiz attempt results
- **UserAnswers**: Detailed response tracking

## 🔐 Default Credentials

The application creates default admin and student accounts:

**Admin Account:**
- Email: `admin@mail.com`
- Password: `admin`

**Student Account:**
- Email: `student@mail.com`
- Password: `student`

## 📊 API Documentation

### Authentication Endpoints
- `POST /api/register` - Register new user
- `POST /api/login` - User login
- `POST /api/logout` - User logout
- `GET /api/me` - Get current user profile

### Admin Endpoints
- `GET /api/admin/users` - List all users
- `POST /api/admin/subjects` - Create subject
- `GET /api/admin/subjects` - List subjects
- `POST /api/admin/chapters` - Create chapter
- `POST /api/admin/quizzes` - Create quiz
- `POST /api/admin/questions` - Create question

### User Endpoints
- `GET /api/subjects` - Browse subjects
- `GET /api/quizzes` - Browse published quizzes
- `POST /api/quizzes/{id}/start` - Start quiz session
- `POST /api/quizzes/{id}/submit` - Submit quiz answers
- `GET /api/users/me/scores` - View my scores

For complete API documentation, see `endpoints.txt`.

## 🔄 Background Tasks

The application includes several Celery tasks:

1. **CSV Export**: Generate and download score reports
2. **Monthly Reports**: Automated email reports to users
3. **Quiz Reminders**: Google Chat notifications for new quizzes

### Starting Background Services
```bash
# Start Redis (required for Celery)
redis-server

# Start Celery worker
celery -A app.celery worker --loglevel=info

# Start Celery beat scheduler
celery -A app.celery beat --loglevel=info
```

## 🧪 Testing

### Running the Application
1. Ensure Redis is running
2. Start the Flask backend
3. Start Celery worker and beat
4. Start the Vue.js frontend
5. Navigate to `http://localhost:5173`
6. Login with default credentials

### Testing Features
- **Admin Flow**: Login as admin → Create subjects/chapters/quizzes → Manage users
- **Student Flow**: Login as student → Browse quizzes → Take assessments → View results
- **Background Tasks**: Test CSV export and email functionality

## 🚨 Troubleshooting

### Common Issues

1. **Database not found**
   ```bash
   cd backend
   python app.py  # This will create the database
   ```

2. **Redis connection error**
   ```bash
   # Make sure Redis is running
   redis-cli ping  # Should return PONG
   ```

3. **CORS errors**
   - Ensure both frontend and backend are running
   - Check CORS configuration in Flask app

4. **Celery tasks not executing**
   - Verify Redis is running
   - Check Celery worker and beat are started
   - Review Celery logs for errors

### Development Notes
- The application uses SQLite for development (consider PostgreSQL for production)
- JWT tokens have a default expiration time
- File uploads are stored in the `static/` directory
- Email functionality requires proper SMTP configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is part of an educational assignment and is intended for academic purposes.

## 👨‍💻 Author

Created as part of the Modern Application Development course project.

## 🆘 Support

For issues and questions, please refer to the project documentation or create an issue in the repository.
