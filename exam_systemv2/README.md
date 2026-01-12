# Online Exam System

A comprehensive online examination system built with FastAPI, Jinja2, SQLite3, and SQLAlchemy. This system allows teachers to create exams, assign them to students, and automatically grade submissions.

## Features

- **Role-Based Access Control**: Admin, Teacher, and Student roles with appropriate permissions
- **Question Bank**: Create and manage multiple choice and true/false questions
- **Exam Management**: Create exams with configurable settings (duration, attempts, grading policy)
- **Student Assignments**: Assign exams to specific students
- **Exam Attempts**: Students can take exams with time limits and question shuffling
- **Automatic Grading**: MCQ questions are automatically graded
- **Result Management**: Results can be released immediately or after exam end
- **Audit Logging**: Track important actions in the system

## Technology Stack

- **Backend**: FastAPI
- **Database**: SQLite3
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Templates**: Jinja2
- **Authentication**: Session-based (HTTPOnly cookies)
- **Password Hashing**: bcrypt (via passlib)

## Installation

### Prerequisites

- Python 3.11 or higher
- pip

### Setup Steps

1. **Clone the repository** (if applicable) or navigate to the project directory

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   python -m pip install --upgrade pip
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **(macOS/Linux) Make scripts executable (if needed)**  
   If you see `permission denied: ./scripts/*.sh`:
   ```bash
   chmod +x scripts/*.sh
   ```
   - Alternatively, you can always run scripts via bash:
   
  ```bash
   bash ./scripts/init_db.sh
bash ./scripts/run_dev.sh
   ```

5. **Configure environment (optional)**  
   Some distributions may **NOT** include `.env.example`.

   - If `.env.example` exists:
     ```bash
     cp .env.example .env
     # Edit .env if needed
     ```
   - If it does **NOT** exist, skip this step.

6. **Initialize the database**:
   ```bash
   ./scripts/init_db.sh
   # Or manually:
   alembic upgrade head
   python -m app.seed.seed_data
   ```

7. **Run the development server**:
   ```bash
   ./scripts/run_dev.sh
   # Or manually:
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

8. **Access the application**:
   - Web UI: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Demo Users

After seeding, you can login with:

- **Admin**: `admin` / `admin123`
- **Teacher**: `teacher` / `teacher123`
- **Student**: `student1` / `student123`

## Usage Flow

### Teacher Workflow

1. **Create Questions**:
   - Navigate to `/teacher/questions`
   - Click "New Question"
   - Fill in question details, options, and tags
   - Save

2. **Create Exam**:
   - Navigate to `/teacher/exams`
   - Click "New Exam"
   - Configure exam settings (duration, grading policy, etc.)
   - Add questions to the exam
   - Publish the exam

3. **Assign Students**:
   - View exam details
   - Assign to students
   - Monitor assignments

4. **Release Results**:
   - After exam period ends (if using AFTER_END policy)
   - Click "Release Results" to make results visible to students

### Student Workflow

1. **View Assignments**:
   - Login and go to `/student/dashboard`
   - See all assigned exams

2. **Start Exam**:
   - Click "Start" on an assigned exam
   - Answer questions (answers auto-save)
   - Submit when finished

3. **View Results**:
   - Results appear based on grading policy
   - IMMEDIATE: Results visible right after submission
   - AFTER_END: Results visible after teacher releases them

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user

### Questions
- `GET /api/questions` - List questions
- `POST /api/questions` - Create question
- `GET /api/questions/{id}` - Get question
- `PUT /api/questions/{id}` - Update question
- `DELETE /api/questions/{id}` - Delete question

### Exams
- `GET /api/exams` - List exams
- `POST /api/exams` - Create exam
- `GET /api/exams/{id}` - Get exam
- `PUT /api/exams/{id}` - Update exam
- `POST /api/exams/{id}/questions` - Add question to exam

### Attempts
- `POST /api/attempts/start` - Start attempt
- `POST /api/attempts/{id}/answer` - Save answer
- `POST /api/attempts/{id}/submit` - Submit attempt
- `GET /api/attempts/{id}` - Get attempt details

### Results
- `GET /api/results/{attempt_id}` - Get result
- `POST /api/results/exams/{exam_id}/release` - Release results

## Project Structure

```
exam_system/
├── app/
│   ├── api/
│   │   └── routes/          # API endpoints
│   ├── core/                # Core utilities (config, security, deps)
│   ├── db/                  # Database configuration
│   ├── models/              # SQLAlchemy models
│   ├── repositories/        # Data access layer
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic layer
│   ├── seed/                # Seed data script
│   ├── web/
│   │   ├── routes/          # Web routes
│   │   └── templates/       # Jinja2 templates
│   └── main.py              # FastAPI application
├── alembic/                 # Migration scripts
├── scripts/                 # Helper scripts
├── requirements.txt
└── README.md
```

## Architecture

The application follows a layered architecture:

1. **Routes Layer**: Handles HTTP requests/responses
2. **Service Layer**: Contains business logic
3. **Repository Layer**: Abstracts database access
4. **Model Layer**: SQLAlchemy ORM models

Key design principles:
- **Dependency Injection**: Services and repositories are injected
- **Time Abstraction**: TimeProvider interface for testability
- **Idempotent Operations**: Start and submit operations are idempotent
- **Transaction Management**: Services manage transaction boundaries

## Database Migrations

To create a new migration:
```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

To reset the database:
```bash
./scripts/reset_db.sh
```

## Development

### Running Tests
(Test suite can be added as needed)

### Code Style
- Type hints are used throughout
- Follow PEP 8
- Use meaningful variable names

## Security Considerations

- Passwords are hashed using bcrypt
- Session cookies are HTTPOnly
- Role-based access control on all routes
- SQL injection protection via SQLAlchemy ORM


## License

This project is provided as-is for educational purposes.

## Support

For issues or questions, please refer to the codebase documentation or create an issue in the repository.

