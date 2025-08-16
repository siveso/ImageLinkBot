from app import db
from datetime import datetime

class UploadedImage(db.Model):
    """Model for tracking uploaded images"""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), unique=True, nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    mime_type = db.Column(db.String(50), nullable=False)
    telegram_user_id = db.Column(db.String(50), nullable=False)
    telegram_username = db.Column(db.String(100), nullable=True)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<UploadedImage {self.filename}>'
    
    @property
    def view_url(self):
        """Get the web view URL for this image"""
        return f"/view/{self.filename}"
    
    @property
    def direct_url(self):
        """Get the direct image URL"""
        return f"/image/{self.filename}"
