# JWT Authentication API - Testing Guide

## Endpoints

All endpoints are prefixed with `/api/` in the development server.

### 1. User Registration (Signup)
**POST** `/api/auth/register/`

Request body:
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "SecurePass123!",
  "password2": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "role": "USER"
}
```

Response (201 Created):
```json
{
  "message": "User registered successfully.",
  "user": {
    "id": 1,
    "username": "newuser",
    "email": "newuser@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "USER"
  }
}
```

### 2. User Login (Get JWT Token)
**POST** `/api/auth/login/`

Request body:
```json
{
  "username": "newuser",
  "password": "SecurePass123!"
}
```

Response (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 3. Refresh Token
**POST** `/api/auth/token/refresh/`

Request body:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

Response (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## Testing with cURL

### Register a new user:
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123!",
    "password2": "TestPass123!",
    "role": "USER"
  }'
```

### Login and get tokens:
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPass123!"
  }'
```

### Refresh access token:
```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "YOUR_REFRESH_TOKEN"}'
```

## Testing with Python Requests

```python
import requests

# Register
resp = requests.post('http://localhost:8000/api/auth/register/', json={
    'username': 'testuser',
    'email': 'test@example.com',
    'password': 'TestPass123!',
    'password2': 'TestPass123!',
    'role': 'USER'
})
print("Register:", resp.json())

# Login
resp = requests.post('http://localhost:8000/api/auth/login/', json={
    'username': 'testuser',
    'password': 'TestPass123!'
})
tokens = resp.json()
print("Login:", tokens)

# Use access token in requests
headers = {'Authorization': f"Bearer {tokens['access']}"}
# Make authenticated requests with this header
```

## Features

- **Custom User Model**: User model extends AbstractUser with a `role` field (ADMIN or USER)
- **JWT Authentication**: SimpleJWT handles token generation and validation
- **Password Validation**: Built-in Django password validators are enforced
- **User Serialization**: Complete user data available in responses
- **Token Refresh**: Access tokens can be refreshed using refresh tokens
- **Role-based Access**: Users have role-based permissions (ADMIN/USER)

## Running the Server

```bash
# Activate virtual environment
env\Scripts\activate

# Run migrations (if not already done)
python manage.py migrate

# Start development server
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`
