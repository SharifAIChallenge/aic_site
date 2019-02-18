# Sharif AI Challenge 2019 website


## Requirements

*  python version 3.6.3 virtual env,
*  postgresql database (production)

## Installation

Installation is as easy as any other Django site inshallah.

## Test

```
pip install -r requirements/production.txt
python manage.py migrate
python manage.py runserver
```

## UI/UX and management

We used trello to track issues, user strories and tasks. You may request for the trello board if you  are reading this document. 

We held sessions on the UX. We simply copied things from the old site and extracted user stories in sentences in a session. Submodules of the site were defined by the technical head of the event. The site team had almost weekly sessions on the site and had extreme times of development. 


## Architecture

The site contains only the control logic for the games to be run and does communicate with another party named middle brain to run games. AIC_game_runner would be up on the middle brain. The API between can be found [here](https://github.com/SharifAIChallenge/AIC_game_runner). 

## About modeling

### Registration and team management

Here it is a bit confusing and counter intuitive but we think it was the best modeling which met our needs. We have `User`s who register. `Profile` is created for them on registration. `User`s can invite other `User`s to a `Team` for a `Challenge` and after the `Team` is created a `TeamParticipatesInChallenge` is created. For each `User` then if the `User` accepts the invitation we create a `UserAcceptsTeamInChallenge`. It is obvious that if there is a `TeamParticipatesInChallenge` for a `User` without a `UserAcceptsTeamInChallenge` an invitation is shown to the user. 

### Payment

We have used a `Payment` model to show if there is a valid payment for a `TeamParticipatesInChallenge` object. The `fee` feild in the `Challenge` object determines whether the `Challenge` is free to attend or not. Then permissions to access challenges is checked with python decorators with querying `Payment` objects.

### Game

The model `Game` contains informatoin about a specific game logic which such as a token to tell the infrustructure that what `Game` is mentioned in the request. There are `Competition`s in a challenge indicating game units. A `Competition` can be of types double elimination and league. There are some issues with the double elimination to be considered. There is a week design here with the leages with multiple groups due to constraints at the time of development. The weekness is that the `Competitions` are tagged and the `Competitions` which are assumed to be in the same super league are indicated with their common tags. These tags are used to perform scheduling with management commands.

The modeling inside the `Competition`s is quite well defined and extensible. But the implementation has weeknesses and some names such as `depends` field can be confusing. The design was to have dags of `Match`es to represent all types of `Competition`s. This general form can cover leagues, torenoments, eliminations, double eliminations, etc. The edges between `Match`es show that the winner or the loser of the required `Match` should attend the dependant `Match`.

Each `Match` consists of several `SingleMatch`es for each of the maps of the competition. We were careful about it to keep it consistent and all matches have the appropriate `SingleMatch`es. Tht model `SingleMatch` is the equalant for the model `Run` in the infrustructure.

## Buesiness logic and configuration

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

### Continuous integration

#### Deployment

Deployment is done with the aim of travis ci. You can find its logic at .travis.yml

When we were developing this project travis prevented us from performing `ssh` to the production machine so we had to have a deployment server which deployed the site to the production after receiving a web signal. 

Furthure documents and deployment server logic could be found at `deployment/README.md`.

#### Test

Test was automated using travis and the commands to be run were like the commands mentioned at the top of this document. 

### Integration with graphics

The graphic part of the game was a pure js application which loaded a file from local or downloaded a file from the website and played it. So the integration was done simply by adding a page. The path to the file to be downloaded was provided to the script with `GET` parameters.

### SSL configuration

It was done using let's encrypt and the key files were generated manully and was put in the deployment server as secret files. This scenario goes for other secret files such as `SECRET_KEY` settings for Django. 

Be careful to config `nginx` and reverse url generation correctly. At the very first try when whe only enabled SSL for nginx and Django were not aware the callback links generated to be used for the payment gateway were broken to http links. 

All the settings that now are present are necessary for the SSL configuration specifically the `CSRF_TRUSTED_ORIGINS` setting.

## Things to be done next

We think things have priority to be done first. You can find the in issues of this repository. 

## AIC Site 2018 team head note

I am keeping other things as obvious, trivial, straight forward or w/e from being documented and at the time I am writing this document I can not spend more time. Please feel free to contact me to engage this project if you found it useful. 

Ali Asgari - Ramadan 1439
