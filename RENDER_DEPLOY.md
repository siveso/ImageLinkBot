# Render.com ga Deploy Qilish Qo'llanmasi

## Loyihani Deploy Qilish

### 1. GitHub Repository yarating
- GitHub ga bu loyihani yuklang
- Barcha fayllar yuklanganini tekshiring

### 2. Render.com da Web Service yarating
1. [Render.com](https://render.com) ga kiring
2. "New +" tugmasini bosing va "Web Service" ni tanlang
3. GitHub repository ni ulang
4. Quyidagi sozlamalarni kiriting:

**Basic Settings:**
- Name: `telegram-image-bot`
- Runtime: `Python 3`
- Build Command: `pip install -r deploy_requirements.txt`
- Start Command: `gunicorn --bind 0.0.0.0:$PORT main:app`

### 3. Environment Variables ni sozlang
Render dashboard da quyidagi environment variables ni qo'shing:

```
TELEGRAM_BOT_TOKEN=sizning_bot_tokeningiz
SESSION_SECRET=random_secret_key
DATABASE_URL=postgresql://user:password@host:port/database
BASE_URL=https://sizning-app-nomi.onrender.com
```

### 4. PostgreSQL Database yarating
1. Render da "New +" > "PostgreSQL" ni tanlang
2. Database yarating
3. Database connection string ni `DATABASE_URL` ga qo'ying

### 5. Static Files uchun Volume yarating (Opsional)
Render da statik fayllar uchun persistent disk yaratishingiz mumkin.

## Fayllar

Deployment uchun yaratilgan fayllar:
- `render.yaml` - Render konfiguratsiya fayli
- `deploy_requirements.txt` - Python kutubxonalar ro'yxati
- `Procfile` - Web server ishga tushirish buyrug'i
- `runtime.txt` - Python versiyasi

## URL lar

Deploy qilinganidan keyin sizning bot quyidagi URL lar bilan ishlaydi:
- Web sahifa: `https://sizning-app-nomi.onrender.com`
- Rasm URL: `https://sizning-app-nomi.onrender.com/image/filename.jpg`
- Ko'rish sahifasi: `https://sizning-app-nomi.onrender.com/view/filename.jpg`

## Xususiyatlar

✅ **Qo'llab-quvvatlanadigan formatlar:**
- JPG/JPEG
- PNG
- GIF
- WebP

✅ **Xususiyatlar:**
- Doimiy rasm saqlash
- O'zbek tilidagi interfeys
- Telegram bot integratsiyasi
- Web ko'rinish va to'g'ridan-to'g'ri URL lar

## Muammolarni hal qilish

1. **Bot javob bermayapti:** TELEGRAM_BOT_TOKEN to'g'ri o'rnatilganini tekshiring
2. **Rasmlar saqlanmayapti:** DATABASE_URL to'g'ri connection string ekanini tekshiring
3. **URL ishlamayapti:** BASE_URL to'g'ri domainni ko'rsatayotganini tekshiring

Deploy qilgandan keyin botingiz 24/7 ishlaydi!