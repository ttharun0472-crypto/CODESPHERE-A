CREATE TABLE IF NOT EXISTS mcq_interview_attempts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject VARCHAR(60) NOT NULL,
    topic VARCHAR(150) NOT NULL,
    difficulty VARCHAR(20) NOT NULL,
    total_questions INTEGER NOT NULL,
    questions JSON NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'in_progress',
    result JSON,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    CONSTRAINT ck_mcq_attempt_positive_question_count CHECK (total_questions > 0)
);

ALTER TABLE mcq_interview_attempts
    ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP;

CREATE INDEX IF NOT EXISTS ix_mcq_interview_attempts_user_id
    ON mcq_interview_attempts (user_id);

CREATE INDEX IF NOT EXISTS ix_mcq_interview_attempts_status
    ON mcq_interview_attempts (status);

CREATE INDEX IF NOT EXISTS ix_mcq_interview_attempts_user_completed
    ON mcq_interview_attempts (user_id, completed_at);

CREATE UNIQUE INDEX IF NOT EXISTS uq_mcq_interview_attempts_one_active_per_user
    ON mcq_interview_attempts (user_id)
    WHERE status = 'in_progress';
