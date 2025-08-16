import os
import logging
import uuid
import requests
import json
import time
import threading
from datetime import datetime
from PIL import Image
from app import app, db
from models import UploadedImage

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Get bot token from environment
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "your-bot-token-here")
BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000")

# Supported image formats
SUPPORTED_FORMATS = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')

def send_message(chat_id, text):
    """Send message via Telegram Bot API"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, json=data)
        return response.json()
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return None

def get_file_info(file_id):
    """Get file info from Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile"
    data = {'file_id': file_id}
    try:
        response = requests.post(url, json=data)
        return response.json()
    except Exception as e:
        logger.error(f"Error getting file info: {e}")
        return None

def download_file(file_path, local_path):
    """Download file from Telegram servers"""
    url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(local_path, 'wb') as f:
                f.write(response.content)
            return True
        return False
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        return False

def handle_start_command(chat_id):
    """Handle /start command"""
    welcome_message = """🤖 Salom! Men Telegram Image Bot-man!

📸 Menga rasm yuboring va men sizga doimiy web URL beraman.

✅ Qo'llab-quvvatlanadigan formatlar:
• JPG/JPEG
• PNG  
• GIF
• WebP

🔗 Yuklangan rasmlaringiz doimiy ravishda saqlanadi va web orqali ochishingiz mumkin bo'ladi.

Boshlash uchun menga rasm yuboring! 📤"""
    send_message(chat_id, welcome_message)

def handle_photo(message, chat_id, user_id, username):
    """Handle photo uploads"""
    try:
        if 'photo' not in message:
            return
        
        # Get the highest resolution photo
        photo = message['photo'][-1]
        file_id = photo['file_id']
        
        # Get file info
        file_info = get_file_info(file_id)
        if not file_info or not file_info.get('ok'):
            send_message(chat_id, "❌ Rasmni yuklashda xatolik yuz berdi.")
            return
        
        file_path = file_info['result']['file_path']
        file_extension = file_path.split('.')[-1] if '.' in file_path else 'jpg'
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        local_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Download the file
        if not download_file(file_path, local_path):
            send_message(chat_id, "❌ Rasmni yuklashda xatolik yuz berdi.")
            return
        
        # Verify it's a valid image
        try:
            with Image.open(local_path) as img:
                format_str = img.format.lower() if img.format else 'jpeg'
                mime_type = f"image/{format_str}"
                if mime_type not in SUPPORTED_FORMATS:
                    os.remove(local_path)
                    send_message(chat_id, "❌ Qo'llab-quvvatlanmaydigan rasm formati!")
                    return
        except Exception as e:
            if os.path.exists(local_path):
                os.remove(local_path)
            send_message(chat_id, "❌ Fayl buzilgan yoki rasm emas!")
            return
        
        # Get file size
        file_size = os.path.getsize(local_path)
        
        # Save to database
        with app.app_context():
            image_record = UploadedImage(
                filename=unique_filename,
                original_filename=f"telegram_photo_{file_id}",
                file_size=file_size,
                mime_type=mime_type,
                telegram_user_id=str(user_id),
                telegram_username=username
            )
            db.session.add(image_record)
            db.session.commit()
            
            # Generate URLs
            view_url = f"{BASE_URL}/view/{unique_filename}"
            direct_url = f"{BASE_URL}/image/{unique_filename}"
        
        # Send success message with URLs
        success_message = f"""✅ Rasm muvaffaqiyatli yuklandi!

🔗 Web sahifada ko'rish:
{view_url}

📎 To'g'ridan-to'g'ri rasm URL:
{direct_url}

💾 Fayl ma'lumotlari:
• Hajmi: {file_size / 1024:.1f} KB
• Format: {mime_type}
• Yuklangan: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Bu URL lar doimiy va hech qachon o'chmaydi! 🎉"""
        
        send_message(chat_id, success_message)
        logger.info(f"Image uploaded successfully: {unique_filename} by user {user_id}")
        
    except Exception as e:
        logger.error(f"Error handling photo: {str(e)}")
        send_message(chat_id, "❌ Rasmni yuklashda xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")

def handle_help_message(chat_id):
    """Handle help/other messages"""
    help_message = """📸 Menga rasm yuboring!

✅ Qo'llab-quvvatlanadigan formatlar:
• JPG/JPEG
• PNG  
• GIF
• WebP

📤 Rasmni fayl sifatida yoki oddiy rasm sifatida yuborishingiz mumkin.

/start - Botni qayta ishga tushirish"""
    send_message(chat_id, help_message)

def process_update(update):
    """Process incoming Telegram update"""
    try:
        if 'message' not in update:
            return
        
        message = update['message']
        chat_id = message['chat']['id']
        user_id = message['from']['id']
        username = message['from'].get('username', 'Unknown')
        
        # Handle commands
        if 'text' in message:
            text = message['text'].strip()
            if text.startswith('/start'):
                handle_start_command(chat_id)
                return
            else:
                handle_help_message(chat_id)
                return
        
        # Handle photos
        if 'photo' in message:
            handle_photo(message, chat_id, user_id, username)
            return
        
        # Default response for other message types
        handle_help_message(chat_id)
        
    except Exception as e:
        logger.error(f"Error processing update: {e}")

def get_updates(offset=0):
    """Get updates from Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {
        'offset': offset,
        'timeout': 30,
        'allowed_updates': ['message']
    }
    try:
        response = requests.get(url, params=params, timeout=35)
        return response.json()
    except Exception as e:
        logger.error(f"Error getting updates: {e}")
        return None

def polling_loop():
    """Main polling loop for the bot"""
    logger.info("Starting Telegram bot polling...")
    offset = 0
    
    while True:
        try:
            updates = get_updates(offset)
            if updates and updates.get('ok'):
                for update in updates['result']:
                    try:
                        process_update(update)
                        offset = update['update_id'] + 1
                    except Exception as e:
                        logger.error(f"Error processing update {update.get('update_id')}: {e}")
            else:
                time.sleep(1)
        except Exception as e:
            logger.error(f"Error in polling loop: {e}")
            time.sleep(5)

def start_bot():
    """Start the Telegram bot"""
    try:
        if BOT_TOKEN == "your-bot-token-here":
            logger.error("TELEGRAM_BOT_TOKEN not set!")
            return
        
        logger.info("Starting Telegram bot...")
        polling_loop()
    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")