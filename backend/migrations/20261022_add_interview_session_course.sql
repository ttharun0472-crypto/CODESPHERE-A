ALTER TABLE interview_sessions
    ADD COLUMN IF NOT EXISTS course_id INTEGER
        REFERENCES courses(id) ON DELETE SET NULL;

ALTER TABLE interview_sessions
    ADD COLUMN IF NOT EXISTS course_title VARCHAR(150);

CREATE INDEX IF NOT EXISTS ix_interview_sessions_course_id
    ON interview_sessions (course_id);
