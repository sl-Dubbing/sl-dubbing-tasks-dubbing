# models.pysl-dubbing-tasks-dubbing — V4.0 (Microservices)
"""🗄️ Database models - 3 job types"""
import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class DubbingJob(db.Model):
    """🎬 Job الدبلجة"""
    __tablename__ = 'dubbing_jobs'
    id = db.Column(db.String(64), primary_key=True, default=lambda: uuid.uuid4().hex)
    user_id = db.Column(db.String(128), nullable=False, index=True)
    language = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), default='pending', index=True)
    output_url = db.Column(db.Text)
    error = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TTSJob(db.Model):
    """🎤 Job تحويل النص لصوت"""
    __tablename__ = 'tts_jobs'
    id = db.Column(db.String(64), primary_key=True, default=lambda: uuid.uuid4().hex)
    user_id = db.Column(db.String(128), nullable=False, index=True)
    text = db.Column(db.String(255))  # أول 200 حرف فقط للسجل
    lang = db.Column(db.String(10))
    status = db.Column(db.String(20), default='pending', index=True)
    output_url = db.Column(db.Text)
    error = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class STTJob(db.Model):
    """🎙️ Job تحويل الصوت لنص"""
    __tablename__ = 'stt_jobs'
    id = db.Column(db.String(64), primary_key=True, default=lambda: uuid.uuid4().hex)
    user_id = db.Column(db.String(128), nullable=False, index=True)
    lang = db.Column(db.String(10))
    status = db.Column(db.String(20), default='pending', index=True)
    output_text = db.Column(db.Text)  # النص الناتج
    output_url = db.Column(db.Text)   # SRT/VTT file
    error = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CreditTransaction(db.Model):
    """💰 سجل المعاملات"""
    __tablename__ = 'credit_transactions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(128), nullable=False, index=True)
    amount = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(255))
    job_id = db.Column(db.String(64), index=True)
    job_type = db.Column(db.String(20))  # dub | tts | stt
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
