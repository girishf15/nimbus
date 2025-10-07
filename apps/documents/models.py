from datetime import datetime
import uuid
from typing import Optional

try:
    # Prefer the project's global db if available
    from nimbus.models import db
except Exception:
    try:
        from models import db  # fallback
    except Exception:
        # Last resort: local SQLAlchemy instance (won't be initialized by app)
        from flask_sqlalchemy import SQLAlchemy

        db = SQLAlchemy()


def gen_uuid():
    return str(uuid.uuid4())


class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.String, primary_key=True, default=gen_uuid)
    filename = db.Column(db.String, nullable=False)
    uploader = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    enabled = db.Column(db.Boolean, default=False)
    parsing_status = db.Column(db.String, default='Unparsed')
    size = db.Column(db.Integer, nullable=True)
    file_path = db.Column(db.String, nullable=True)

    def as_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'uploader': self.uploader,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'enabled': self.enabled,
            'parsing_status': self.parsing_status,
            'size': self.size,
            'file_path': self.file_path,
        }
