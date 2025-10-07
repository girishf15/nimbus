-- Enable pgvector extension (image already includes pgvector but keep safe)
CREATE EXTENSION IF NOT EXISTS vector;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  role TEXT DEFAULT 'user'
);

-- Insert default admin user (password: admin123 - CHANGE IMMEDIATELY IN PRODUCTION!)
-- This is a weak default password for initial setup only
-- Generate new hash with: python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your-secure-password'))"
INSERT INTO users (username, password_hash, role) VALUES (
  'admin', '$2b$12$LYvmEzFcXxFyQQgF8jQ8YOHmVyX9qcuWlQGFXNJKQWYGjQE8FqKJ6', 'admin'
)
ON CONFLICT (username) DO NOTHING;
