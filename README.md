# BotWork-1.1.0

![logo](https://github.com/WoLand-Q/BotWork-1.1.0/assets/72334898/c6bceb5c-a3e2-41ea-8925-74aee1cd218b)


BotWork-1.1.0 — это бот для Telegram, разработанный для команды Смарт Кафе от компании Syrve. Бот предназначен для автоматизации рутинных задач администрирования сотрудников и облегчения коммуникации между управляющими и персоналом.

## Основные функции

### Для администратора:

- `/start` - Начало работы с ботом.
- `/upload_schedule` - Загрузка графика работы сотрудников.
- `/view_schedule` - Просмотр текущего графика работы.
- `/remind today|tomorrow` - Напоминание о сменах на сегодня или завтра.
- `/add_employee` - Добавление нового сотрудника.
- `/delete_employee` - Удаление сотрудника из системы.
- `/choose_employee` - Просмотр списка сотрудников.
- `/add_shift_template` - Добавление шаблона времени для смен.
- `/deletenote` - Удаление статьи (необходим ID статьи).

### Для сотрудника:

- `/add_comment` - Добавление комментария к заявке.
- `/new_ticket` - Создание новой заявки для разработчика.
- `/search` - Поиск статьи в базе знаний.
- `/getnotes` - Просмотр доступных статей.
- `/savenote` - Сохранение заметки в виде статьи.
- `/view_schedule` - Просмотр графика работы.
- `/unbind` - Удаление привязки аккаунта Telegram к сотруднику.
- `/schedule` - Привязка аккаунта Telegram к инициалам сотрудника и просмотр графика.
- `/set_preferences` - Отправка пожеланий по графику работы.

## Интерфейс пользователя

Бот предоставляет удобный интерфейс для взаимодействия как с администраторами, так и с сотрудниками. Например, команда `/choose_employee` позволяет администратору видеть список всех сотрудников и устанавливать график на месяц вперёд, учитывая различное количество дней в месяце.

![График работы](https://github.com/WoLand-Q/BotWork-1.1.0/assets/72334898/45a62efd-000c-465c-996c-0bc3dd444ecb)
![График работы](https://github.com/WoLand-Q/BotWork-1.1.0/assets/72334898/d606651a-ce3c-47f6-8e9c-4fe30e7b2c4a)
![График работы](https://github.com/WoLand-Q/BotWork-1.1.0/assets/72334898/5a96bb76-98e3-4405-bee7-be49f6c78e11)


Кроме того, есть возможность загрузки графика работы в виде изображения через команду `/upload_schedule`.

## База знаний

Бот включает в себя функционал базы знаний, позволяя создавать, просматривать и удалять статьи прямо из Telegram.

## Установка графика работы

Сотрудники могут привязывать свой аккаунт Telegram к своим инициалам, что сохранены в базе данных, и смотреть установленный график на весь месяц.

## Обратная связь и техническая поддержка

При возникновении технических проблем с ботом сотрудники могут создавать заявки разработчику через команду `/new_ticket`.

## Как начать использовать

Для начала работы с ботом достаточно отправить ему команду `/start` и следовать дальнейшим инструкциям.

---

Этот документ предназначен для помощи в освоении и использовании бота BotWork-1.1.0. Для получения более подробной информации и технической поддержки обращайтесь к разработчикам.
