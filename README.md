# Quiz Platform API

A REST API backend for a quiz platform with role-based access control, JWT authentication, and automatic scoring.

## Features

- **JWT Authentication** - Secure token-based authentication
- **Role-Based Access Control** - Separate ADMIN and USER roles
- **Automatic Scoring** - Quiz submissions scored automatically
- **Quiz Management** - Admins can create/update/duplicate quizzes
- **Question & Options** - Support for multiple-choice questions
- **Submission History** - Users can track their quiz attempts
- **Pass/Fail System** - Configurable passing scores

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install django djangorestframework djangorestframework-simplejwt psycopg2-binary
```

### 2. Database Configuration

Create PostgreSQL database:
```sql
CREATE DATABASE quizapp;
```

Update `quizapp/settings.py` with your database credentials:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'quizapp',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 3. Run Migrations
```bash
python manage.py migrate
```

### 4. Create Admin User

Option 1 - Using createsuperuser:
```bash
python manage.py createsuperuser
```
Enter username, email, and password. Then set role:
```bash
python manage.py shell
>>> from quiz.models import User
>>> admin = User.objects.get(username='your_username')
>>> admin.role = 'ADMIN'
>>> admin.save()
>>> exit()
```

Option 2 - Using registration endpoint (see API section below)

### 5. Start Server
```bash
python manage.py runserver
```

API available at: `http://localhost:8000/api/`

---

## API Endpoints

### Authentication (Public)
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login and get JWT tokens
- `POST /api/auth/token/refresh/` - Refresh access token

### Admin Endpoints (Admin Role Required)
- `GET/POST /api/admin/categories/` - List/Create categories
- `GET/PUT/PATCH/DELETE /api/admin/categories/{id}/` - Manage category
- `GET/POST /api/admin/quizzes/` - List/Create quizzes
- `GET/PUT/PATCH/DELETE /api/admin/quizzes/{id}/` - Manage quiz
- `POST /api/admin/quizzes/{id}/duplicate/` - Duplicate quiz with all questions
- `GET/POST /api/admin/questions/` - List/Create questions
- `GET/PUT/PATCH/DELETE /api/admin/questions/{id}/` - Manage question
- `POST /api/admin/questions/{id}/add_option/` - Add option to question

### User Endpoints (User Role Required)
- `GET /api/quizzes/active/` - List active quizzes
- `GET /api/quizzes/{id}/` - Get quiz details with questions
- `POST /api/quizzes/submit/` - Submit quiz answers
- `GET /api/quizzes/my-submissions/` - Get user's submission history
- `GET /api/quizzes/submissions/{id}/` - Get submission details

---

## API Usage Examples

### Authentication

**Register Admin:**
```
POST http://localhost:8000/api/auth/register/
Content-Type: application/json

{
  "username": "admin1",
  "email": "admin@example.com",
  "password": "Admin@123",
  "password2": "Admin@123",
  "role": "ADMIN"
}
```

**Register User:**
```
POST http://localhost:8000/api/auth/register/
Content-Type: application/json

{
  "username": "user1",
  "email": "user@example.com",
  "password": "User@123",
  "password2": "User@123",
  "role": "USER"
}
```

**Login:**
```
POST http://localhost:8000/api/auth/login/
Content-Type: application/json

{
  "username": "admin1",
  "password": "Admin@123"
}
```

Response contains `access` and `refresh` tokens. Use access token in Authorization header for subsequent requests:
```
Authorization: Bearer <access_token>
```

### Admin Endpoints

**Create Category:**
```
POST http://localhost:8000/api/admin/categories/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "name": "Python",
  "is_active": true
}
```

Response:
```json
{
  "id": 1,
  "name": "Python",
  "is_active": true,
  "created_at": "2025-11-15T10:00:00Z",
  "updated_at": "2025-11-15T10:00:00Z"
}
```

**Create Quiz:**
```
POST http://localhost:8000/api/admin/quizzes/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "category": 1,
  "title": "Python Basics Quiz",
  "description": "Test your Python knowledge",
  "passing_score": 70,
  "is_active": true
}
```

**Create Question:**
```
POST http://localhost:8000/api/admin/questions/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "quiz": 1,
  "text": "What is Python?",
  "is_active": true
}
```

Response:
```json
{
  "id": 1,
  "quiz": 1,
  "text": "What is Python?",
  "correct_option_id": null,
  "is_active": true,
  "options": [],
  "created_at": "2025-11-15T10:00:00Z",
  "updated_at": "2025-11-15T10:00:00Z"
}
```

**Add Options:**
```
POST http://localhost:8000/api/admin/questions/1/add_option/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "text": "A programming language"
}
```

Response:
```json
{
  "id": 1,
  "text": "A programming language",
  "created_at": "2025-11-15T10:00:00Z",
  "updated_at": "2025-11-15T10:00:00Z"
}
```

Add 4 options total. Repeat with different texts:
- "A programming language"
- "A snake"
- "A database"
- "An operating system"

**Set Correct Answer:**
```
PATCH http://localhost:8000/api/admin/questions/1/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "correct_option_id": 1
}
```

**Duplicate Quiz:**
```
POST http://localhost:8000/api/admin/quizzes/1/duplicate/
Authorization: Bearer <admin_token>
```
Creates a copy of the quiz with all questions and options.

**Activate/Deactivate Quiz:**
```
PATCH http://localhost:8000/api/admin/quizzes/1/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "is_active": false
}
```

**List All Categories:**
```
GET http://localhost:8000/api/admin/categories/
Authorization: Bearer <admin_token>
```

**Update Category:**
```
PUT http://localhost:8000/api/admin/categories/1/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "name": "Python Programming",
  "is_active": true
}
```

### User Endpoints

**View Active Quizzes:**
```
GET http://localhost:8000/api/quizzes/active/
Authorization: Bearer <user_token>
```

**Get Quiz Details:**
```
GET http://localhost:8000/api/quizzes/1/
Authorization: Bearer <user_token>
```
Returns quiz with all questions and options.

**Submit Quiz:**
```
POST http://localhost:8000/api/quizzes/submit/
Authorization: Bearer <user_token>
Content-Type: application/json

{
  "quiz": 1,
  "answers": {
    "1": 5,
    "2": 8
  }
}
```

Format: 
- `quiz`: Quiz ID
- `answers`: Dictionary mapping question IDs to selected option IDs
- All questions must be answered

Response includes:
- `submission.id` - Submission ID
- `submission.score` - Calculated score (0-100)
- `submission.passed` - Whether score meets passing_score
- `submission.submitted_at` - Timestamp

**View Submission History:**
```
GET http://localhost:8000/api/quizzes/my-submissions/
Authorization: Bearer <user_token>
```

**View Specific Submission:**
```
GET http://localhost:8000/api/quizzes/submissions/1/
Authorization: Bearer <user_token>
```

---

## Data Models

### User
- `username` - Unique username
- `email` - Email address
- `role` - Either "ADMIN" or "USER"
- `password` - Hashed password

### Category
- `name` - Category name (unique)
- `is_active` - Active status

### Quiz
- `category` - Foreign key to Category
- `title` - Quiz title
- `description` - Quiz description
- `passing_score` - Minimum score to pass (0-100)
- `is_active` - Active status

### Question
- `quiz` - Foreign key to Quiz
- `text` - Question text
- `correct_option` - Foreign key to Option (correct answer)
- `is_active` - Active status

### Option
- `question` - Foreign key to Question
- `text` - Option text

### Submission
- `user` - Foreign key to User
- `quiz` - Foreign key to Quiz
- `score` - Calculated score (0-100)
- `submitted_at` - Timestamp

### Answer
- `submission` - Foreign key to Submission
- `question` - Foreign key to Question
- `selected_option` - Foreign key to Option
- `is_correct` - Auto-calculated boolean

---

---

## Important Notes

- **IDs**: Always use `id` values from API responses; PostgreSQL IDs don't reset when records are deleted
- **Roles**: Admin users manage quizzes; User role required to take quizzes
- **Permissions**: Admin endpoints return 403 for non-admin users
- **Submissions**: All active questions must be answered
- **Scoring**: Automatic calculation: (correct_answers / total_questions) × 100
- **JWT Tokens**: Access token valid for 60 minutes, refresh token for 24 hours
- **Inactive Content**: Hidden from users but visible to admins

### Common Workflow
1. Create category and save returned `id`
2. Create quiz using category `id`
3. Create questions and add options
4. Set correct answer for each question
5. Activate quiz for users

## Project Structure

```
quizapp/
├── manage.py
├── requirements.txt
├── README.md
├── db.sqlite3 / PostgreSQL
├── quizapp/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── quiz/
    ├── models.py
    ├── serializers.py
    ├── views.py
    ├── urls.py
    ├── permissions.py
    └── admin.py
```

## Technology Stack

- **Django 5.2.8** - Web framework
- **Django REST Framework 3.16.1** - REST API toolkit
- **Simple JWT 5.5.1** - JWT authentication
- **PostgreSQL** - Primary database (SQLite for development)
- **Python 3.11+** - Programming language
