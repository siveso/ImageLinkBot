# Telegram Image Bot

Python va Flask yordamida yuklangan rasmlarni doimiy web URL ga aylantiradigan Telegram bot.

## Xususiyatlar

- 📸 Telegram orqali rasm yuklash
- 🔗 Doimiy URL yaratish (rasmlar hech qachon o'chmaydi)
- 🌐 Web sahifada ko'rish imkoniyati
- 🏠 O'zbek tilidagi interfeys
- 📱 Responsive dizayn

## Qo'llab-quvvatlanadigan formatlar

- JPG/JPEG
- PNG
- GIF
- WebP

## O'rnatish

### Lokal muhitda

1. Repository ni klonlang:
```bash
git clone <repository-url>
cd telegram-image-bot
```

2. Virtual environment yarating:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# yoki
venv\Scripts\activate  # Windows
```

3. Dependency larni o'rnating:
```bash
pip install -r deploy_requirements.txt
```

4. Environment variables ni sozlang:
```bash
export TELEGRAM_BOT_TOKEN="sizning_bot_tokeningiz"
export DATABASE_URL="sqlite:///telegram_images.db"
export SESSION_SECRET="random_secret_key"
export BASE_URL="http://localhost:5000"
```

5. Ilova ni ishga tushiring:
```bash
python main.py
```

### Render.com ga deploy qilish

`RENDER_DEPLOY.md` faylini o'qing.

## Foydalanish

1. Telegram botni @Rasmurl_bot dan toping
2. `/start` buyrug'ini yuboring
3. Rasm yuboring
4. Bot sizga 2 ta URL beradi:
   - Web sahifada ko'rish uchun
   - To'g'ridan-to'g'ri rasm uchun

## Loyiha tuzilishi

```
telegram-image-bot/
├── app.py              # Flask ilovasi
├── main.py             # Kirish nuqtasi
├── models.py           # Database modellari
├── telegram_bot.py     # Telegram bot logikasi
├── templates/          # HTML shablonlari
│   ├── image.html
│   └── error.html
├── static/
│   └── uploads/        # Yuklangan rasmlar
├── deploy_requirements.txt
├── Procfile
├── runtime.txt
├── render.yaml
└── README.md
```

## URL lar

- Ana sahifa: `/`
- Rasm ko'rish: `/view/<filename>`
- To'g'ridan-to'g'ri rasm: `/image/<filename>`

## Xavfsizlik

- Rasm formatlarini tekshirish
- Fayl hajmini cheklash
- SQL injection himoyasi
- XSS himoyasi

## Litsenziya

MIT

## Muallif

Telegram Image Bot - O'zbek tilidagi rasm yuklash boti