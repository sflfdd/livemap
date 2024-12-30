# LiveMap Palestine 🗺️

خريطة تفاعلية لعرض الأحداث في فلسطين مباشرةً

## المميزات 🌟

- خريطة تفاعلية لعرض الأحداث
- تحديثات مباشرة للأخبار
- دعم كامل للغة العربية
- واجهة مستخدم سهلة وبسيطة
- وضع النهار والليل
- نظام مصادقة آمن
- تصميم متجاوب مع جميع الأجهزة

## المتطلبات 📋

- Python 3.8+
- pip
- PostgreSQL (اختياري، يمكن استخدام SQLite)
- Node.js (للتطوير)

## التثبيت 🚀

1. استنساخ المشروع:
```bash
git clone https://github.com/yourusername/livemap-palestine.git
cd livemap-palestine
```

2. إنشاء بيئة Python افتراضية:
```bash
python -m venv venv
source venv/bin/activate  # على Linux/Mac
venv\Scripts\activate     # على Windows
```

3. تثبيت المتطلبات:
```bash
pip install -r requirements.txt
```

4. إعداد ملف البيئة:
```bash
cp .env.example .env
# قم بتعديل الإعدادات في ملف .env
```

5. تهيئة قاعدة البيانات:
```bash
python init_db.py
```

6. تشغيل التطبيق:
```bash
python app.py
```

## هيكل المشروع 📁

```
livemap/
├── app/                    # التطبيق الرئيسي
│   ├── __init__.py
│   ├── models/            # نماذج قاعدة البيانات
│   ├── routes/            # مسارات API
│   ├── services/          # خدمات التطبيق
│   └── utils/             # أدوات مساعدة
├── static/                # الملفات الثابتة
│   ├── css/
│   ├── js/
│   └── img/
├── templates/             # قوالب HTML
├── tests/                 # اختبارات
├── config.py             # إعدادات التطبيق
├── requirements.txt      # متطلبات Python
└── .env                  # متغيرات البيئة
```

## المساهمة 🤝

نرحب بمساهماتكم! يرجى اتباع الخطوات التالية:

1. Fork المشروع
2. إنشاء فرع للميزة الجديدة
3. تقديم pull request

## الترخيص 📄

هذا المشروع مرخص تحت رخصة MIT - انظر ملف [LICENSE](LICENSE) للتفاصيل.

## الاتصال 📧

- الموقع: [https://livemap-palestine.example.com](https://livemap-palestine.example.com)
- البريد الإلكتروني: support@livemap-palestine.example.com
- تويتر: [@LiveMapPalestine](https://twitter.com/LiveMapPalestine)
