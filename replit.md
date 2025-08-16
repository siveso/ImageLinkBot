# Overview

This is a Telegram Image Bot web application that allows users to upload images through a Telegram bot and receive permanent web URLs to access those images. The system consists of a Flask web application that serves uploaded images and a Telegram bot that handles image uploads from users. Images are stored locally in the file system and metadata is tracked in a database.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Web Application Architecture
- **Framework**: Flask web application with SQLAlchemy ORM for database operations
- **Database**: SQLite by default (configurable via DATABASE_URL environment variable)
- **File Storage**: Local file system storage in `static/uploads` directory
- **Templates**: Jinja2 templating with Bootstrap for responsive UI
- **Middleware**: ProxyFix for handling reverse proxy headers

## Database Schema
- **UploadedImage Model**: Tracks image metadata including filename, original filename, file size, MIME type, Telegram user information, and upload timestamps
- **URL Generation**: Provides both view URLs (`/view/{filename}`) and direct image URLs (`/image/{filename}`)

## Bot Architecture
- **Telegram Integration**: Uses python-telegram-bot library for handling bot interactions
- **Image Processing**: PIL (Python Imaging Library) for image manipulation
- **Supported Formats**: JPEG, PNG, GIF, and WebP image formats
- **File Handling**: Downloads images from Telegram servers and stores them locally with UUID-based filenames

## Authentication & Security
- **No User Authentication**: Public access to uploaded images via generated URLs
- **Session Management**: Flask sessions with configurable secret key
- **File Validation**: MIME type checking for supported image formats

## Error Handling
- **404 Handling**: Custom error pages for missing images
- **Logging**: Comprehensive logging for debugging and monitoring
- **Database Connection**: Connection pooling with health checks and automatic reconnection

# External Dependencies

## Third-Party Libraries
- **Flask**: Web framework and SQLAlchemy for ORM
- **python-telegram-bot**: Telegram Bot API integration
- **PIL (Pillow)**: Image processing and validation
- **requests**: HTTP client for downloading images from Telegram
- **Bootstrap**: Frontend CSS framework (via CDN)
- **Font Awesome**: Icon library (via CDN)

## Environment Variables
- **TELEGRAM_BOT_TOKEN**: Required for Telegram bot authentication
- **DATABASE_URL**: Database connection string (defaults to SQLite)
- **BASE_URL**: Application base URL for generating image links
- **SESSION_SECRET**: Flask session encryption key

## External Services
- **Telegram Bot API**: For receiving and processing user messages and images
- **CDN Services**: Bootstrap and Font Awesome served from external CDNs