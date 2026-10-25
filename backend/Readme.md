# CodeSphere Backend

Backend API for the CodeSphere student platform.

## Technology

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- JWT Authentication
- bcrypt

## AI mock interviews

Authenticated students can select courses from the Learning Module, create and
resume interviews, submit answers for structured AI evaluation, and review their
own results and history. Technical and mixed questions are grounded in the
selected course's lessons, topics, and LMS question bank. HR and communication
interviews use a built-in general question bank. If AI question generation is
unavailable, curated course-based defaults are used. Answer evaluation still
requires the existing `GEMINI_API_KEY` backend environment variable and reports
provider errors explicitly. No new Python package is required.

Session records are stored in the `interview_sessions` table. Existing databases
must run `migrations/20261022_add_interview_session_course.sql` to add the
nullable course reference and title snapshot. The migration preserves existing
sessions. `Base.metadata.create_all()` creates new tables but does not alter an
existing table to add columns.

## Email OTP sign-in

`POST /auth/otp/request` sends a six-digit code to a registered account and
`POST /auth/otp/verify` issues the normal access and refresh tokens only after
successful verification. Codes expire after five minutes, are stored as
keyed HMAC digests, allow five incorrect attempts, and are single-use. Resends
have a 60-second cooldown and are limited to five requests per email per hour.
The `email_otp_challenges` table is created by the existing SQLAlchemy
`Base.metadata.create_all()` startup call; it does not alter the users table.

Configure a real SMTP provider in `backend/.env` before using sign-in:

```dotenv
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-sender@example.com
SMTP_PASSWORD=your-provider-app-password
SMTP_FROM_EMAIL=your-sender@example.com
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

Use provider-issued credentials (for Gmail, an App Password), keep them only in
the backend environment, and never commit the file. For implicit TLS such as
port 465, set `SMTP_USE_SSL=true` and `SMTP_USE_TLS=false`. When SMTP is not
configured, the request endpoint returns an explicit service-unavailable error;
it does not claim that an email was sent. Password-only `POST /auth/login` is
disabled. JWTs now include an OTP-verification claim; access and refresh tokens
issued before this change must be replaced by signing in again with an email
code.

CORS middleware wraps the FastAPI application so browser requests can read
responses from both normal endpoints and backend error handlers.

## Project Structure

```text
Backend/
├── app/
│   ├── config/
│   ├── middleware/
│   ├── models/
│   ├── routes/
│   ├── schemas/
│   ├── services/
│   ├── utils/
│   ├── dependencies.py
│   └── main.py
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md