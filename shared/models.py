# shared/models.py — Dubbing worker
"""Database models for dubbing Celery worker."""
import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class DubbingJob(db.Model):
    """Dubbing pipeline job."""
    __tablename__ = 'dubbing_jobs'

    id = db.Column(db.String(64), primary_key=True, default=lambda: uuid.uuid4().hex)
    user_id = db.Column(db.String(128), nullable=False, index=True)
    language = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), default='pending', index=True)
    output_url = db.Column(db.Text)
    error = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
