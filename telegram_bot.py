import os
import logging
import uuid
import requests
from datetime import datetime
from PIL import Image
from app import app, db
from models import UploadedImage

# Import telegram components
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Get bot token from environment
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "your-bot-token-here")
BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000")

# Supported image formats
SUPPORTED_FORMATS = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_message = """
🤖 Salom! Men Telegram Image Bot-man!

📸 Menga rasm yuboring va men sizga doimiy web URL beraman.

✅ Qo'llab-quvvatlanadigan formatlar:
• JPG/JPEG
• PNG  
• GIF
• WebP

🔗 Yuklangan rasmlaringiz doimiy ravishda saqlanadi va web orqali ochishingiz mumkin bo'ladi.

Boshlash uchun menga rasm yuboring! 📤
    """
    await update.message.reply_text(welcome_message)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo uploads"""
    try:
        user = update.effective_user
        photo = update.message.photo[-1]  # Get the highest resolution photo
        
        # Get file info
        file = await context.bot.get_file(photo.file_id)
        
        # Generate unique filename
        file_extension = file.file_path.split('.')[-1] if '.' in file.file_path else 'jpg'
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Download the file
        await file.download_to_drive(file_path)
        
        # Verify it's a valid image
        try:
            with Image.open(file_path) as img:
                format_str = img.format.lower() if img.format else 'jpeg'
                mime_type = f"image/{format_str}"
                if mime_type not in SUPPORTED_FORMATS:
                    os.remove(file_path)
                    await update.message.reply_text("❌ Qo'llab-quvvatlanmaydigan rasm formati!")
                    return
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            await update.message.reply_text("❌ Fayl buzilgan yoki rasm emas!")
            return
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Save to database
        with app.app_context():
            image_record = UploadedImage(
                filename=unique_filename,
                original_filename=f"telegram_photo_{photo.file_id}",
                file_size=file_size,
                mime_type=mime_type,
                telegram_user_id=str(user.id),
                telegram_username=user.username
            )
            db.session.add(image_record)
            db.session.commit()
            
            # Generate URLs
            view_url = f"{BASE_URL}/view/{unique_filename}"
            direct_url = f"{BASE_URL}/image/{unique_filename}"
        
        # Send success message with URLs
        success_message = f"""
✅ Rasm muvaffaqiyatli yuklandi!

🔗 Web sahifada ko'rish:
{view_url}

📎 To'g'ridan-to'g'ri rasm URL:
{direct_url}

💾 Fayl ma'lumotlari:
• Hajmi: {file_size / 1024:.1f} KB
• Format: {mime_type}
• Yuklangan: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Bu URL lar doimiy va hech qachon o'chmaydi! 🎉
        """
        
        await update.message.reply_text(success_message)
        logger.info(f"Image uploaded successfully: {unique_filename} by user {user.id}")
        
    except Exception as e:
        logger.error(f"Error handling photo: {str(e)}")
        await update.message.reply_text("❌ Rasmni yuklashda xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle document uploads (for image files sent as documents)"""
    try:
        user = update.effective_user
        document = update.message.document
        
        # Check if it's an image
        if not document.mime_type or not document.mime_type.startswith('image/'):
            await update.message.reply_text("❌ Faqat rasm fayllarini yuklash mumkin!")
            return
        
        if document.mime_type not in SUPPORTED_FORMATS:
            await update.message.reply_text("❌ Qo'llab-quvvatlanmaydigan rasm formati!")
            return
        
        # Check file size (max 20MB)
        if document.file_size > 20 * 1024 * 1024:
            await update.message.reply_text("❌ Fayl hajmi juda katta! Maksimal hajm: 20MB")
            return
        
        # Get file info
        file = await context.bot.get_file(document.file_id)
        
        # Generate unique filename
        file_extension = document.file_name.split('.')[-1] if '.' in document.file_name else 'jpg'
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Download the file
        await file.download_to_drive(file_path)
        
        # Verify it's a valid image
        try:
            with Image.open(file_path) as img:
                # Image is valid
                pass
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            await update.message.reply_text("❌ Fayl buzilgan yoki rasm emas!")
            return
        
        # Save to database
        with app.app_context():
            image_record = UploadedImage(
                filename=unique_filename,
                original_filename=document.file_name,
                file_size=document.file_size,
                mime_type=document.mime_type,
                telegram_user_id=str(user.id),
                telegram_username=user.username
            )
            db.session.add(image_record)
            db.session.commit()
            
            # Generate URLs
            view_url = f"{BASE_URL}/view/{unique_filename}"
            direct_url = f"{BASE_URL}/image/{unique_filename}"
        
        # Send success message with URLs
        success_message = f"""
✅ Rasm muvaffaqiyatli yuklandi!

🔗 Web sahifada ko'rish:
{view_url}

📎 To'g'ridan-to'g'ri rasm URL:
{direct_url}

💾 Fayl ma'lumotlari:
• Nomi: {document.file_name}
• Hajmi: {document.file_size / 1024:.1f} KB
• Format: {document.mime_type}
• Yuklangan: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Bu URL lar doimiy va hech qachon o'chmaydi! 🎉
        """
        
        await update.message.reply_text(success_message)
        logger.info(f"Document uploaded successfully: {unique_filename} by user {user.id}")
        
    except Exception as e:
        logger.error(f"Error handling document: {str(e)}")
        await update.message.reply_text("❌ Faylni yuklashda xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")

async def handle_other_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle other types of messages"""
    help_message = """
📸 Menga rasm yuboring!

✅ Qo'llab-quvvatlanadigan formatlar:
• JPG/JPEG
• PNG  
• GIF
• WebP

📤 Rasmni fayl sifatida yoki oddiy rasm sifatida yuborishingiz mumkin.

/start - Botni qayta ishga tushirish
    """
    await update.message.reply_text(help_message)

def start_bot():
    """Start the Telegram bot"""
    try:
        # Create application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
        application.add_handler(MessageHandler(filters.Document.IMAGE, handle_document))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_other_messages))
        
        # Start the bot
        logger.info("Starting Telegram bot...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")
