import os
import logging
from flask import Flask, render_template, send_from_directory, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
import threading

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///telegram_images.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Create upload directory if it doesn't exist
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

with app.app_context():
    # Import models to create tables
    import models
    db.create_all()

@app.route('/')
def index():
    """Home page with bot information"""
    return render_template('image.html', 
                         title="Telegram Image Bot", 
                         message="Telegram botga rasm yuboring va doimiy URL oling!")

@app.route('/image/<filename>')
def serve_image(filename):
    """Serve uploaded images"""
    try:
        from models import UploadedImage
        
        # Check if image exists in database
        image_record = UploadedImage.query.filter_by(filename=filename).first()
        if not image_record:
            abort(404)
        
        # Serve the file
        return send_from_directory(UPLOAD_FOLDER, filename)
    except Exception as e:
        logging.error(f"Error serving image {filename}: {str(e)}")
        return render_template('error.html', 
                             title="Rasm topilmadi", 
                             message="Siz qidirayotgan rasm mavjud emas.")

@app.route('/view/<filename>')
def view_image(filename):
    """View image in a web page"""
    try:
        from models import UploadedImage
        
        # Check if image exists in database
        image_record = UploadedImage.query.filter_by(filename=filename).first()
        if not image_record:
            return render_template('error.html', 
                                 title="Rasm topilmadi", 
                                 message="Siz qidirayotgan rasm mavjud emas.")
        
        image_url = f"/image/{filename}"
        return render_template('image.html', 
                             title=f"Yuklangan rasm: {filename}",
                             image_url=image_url,
                             filename=filename,
                             upload_date=image_record.upload_date)
    except Exception as e:
        logging.error(f"Error viewing image {filename}: {str(e)}")
        return render_template('error.html', 
                             title="Xatolik", 
                             message="Rasmni yuklashda xatolik yuz berdi.")

# Start Telegram bot in a separate thread
def start_telegram_bot():
    try:
        from telegram_bot import start_bot
        start_bot()
    except Exception as e:
        logging.error(f"Error starting Telegram bot: {str(e)}")

# Start the bot when the app starts
bot_thread = threading.Thread(target=start_telegram_bot, daemon=True)
bot_thread.start()
