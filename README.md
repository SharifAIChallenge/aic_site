# Sharif AI Challenge 2018 webite

---

## Requirements

*  python version 3.6.3 virtual env,
*  postgresql database (production)


## Test

```
pip install -r requirements/production.txt
python manage.py migrate
python manage.py runserver
```

## Explanations

### Persian docs obtained from developers 

<p dir='rtl' align='right'>
قسمت بلاگ :<br>
توضیح :<br>
وبلاگ و پرسش و پاسخ سایت
پیکربندی:<br>
از وبلاگ zinnia استفاده شده‌است که تغییراتی در آن انجام شده‌است و اپ آن در SETTINGS اضافه شده‌است. برای کامنت‌ها هم از django threaded comments استفاده شده‌است.<br>
نکات پیاده‌سازی :<br>
در پوشه‌ی templates قابلیت تغییر قالب زینیا و کامنت‌ها وجود دارد.  که عمده‌ی تغییرات در فایل entry_detail_base.html زینیا انجام شده‌است. برای کامنت ها هم تغییراتی در پوشه‌ی comments در تمپلیت‌ها انجام شده‌است.
</p>


<p dir='rtl' align='right'>
داخل apps/game/templates رابط کاربری جدول های دوحذفی و تک حذفی وجود دارد که table ها با سمنتیک زده شده‌اند و جدول دو حذفی هم تقریبن css خالص است که هر ستون عمودی آن یک لایه است و امکان گذاشتن جدول تا ۵ لایه یا ۳۲ تیم امکان نمایش را دارد!
</p>

<p dir='rtl' align='right'>
قسمت سابمیشن در پنل:<br>
توضیح:‌ <br>
قستی از پنل است که کاربران می‌توانند کدهای خود را ارسال کنند. <br>
پیکربندی: <br>
به صورتی پیاده‌سازی شده است که ‌‍‍`ENABLE_SUBMISSION` در تنظیمات امکان ارسال فایل را کنترل می‌کند. در Challenge مربوط هم فیلدی به نام  is_submission_open وجود دارد که به طور کلی امکان سابمیشن از جمله قابلیت تعویض کد نهایی را هم غیر فعال می‌کند. <br>
نکات پیاده‌سازی:‌ <br>
در پیاده سازی این قسمت از امکان ajax ای که semantic ui دارد استفاده کردیم. برای صفحه‌بندی ارسال‌ها هم از ‌‌ Paginator  جنگو در ویوی مربوط استفاده کردیم. فایلهای ارسال شده را هم با نام خودشان به علاوه رشته ای تصادفی ذخیره می کنیم. 
نحوه نهایی شدن یک ارسال را می‌توانید با مطالعه طراحی و مدلسازی سایت و جزئیات ارتباط سایت و زیرساخت  ببینید.
</p>

### Deployment

Deployment is done with the aim of travis ci. You can find its logic at .travis.yml

When we were developing this project travis prevented us from performing `ssh` to the production machine so we had to have a deployment server which deployed the site to the production after receiving a web signal. 

Furthure documents and deployment server logic could be found at `deployment/README.md`.

### Integration with graphics

The graphic part of the game was a pure js application which loaded a file from local or downloaded a file from the website and played it. So the integration was done simply by adding a page. The path to the file to be downloaded was provided to the script with `GET` parameters.

### SSL configuration

It was done using let's encrypt and the key files were generated manully and was put in the deployment server as secret files. This scenario goes for other secret files such as `SECRET_KEY` settings for Django. 

