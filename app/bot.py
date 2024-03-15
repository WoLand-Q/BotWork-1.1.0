from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime
from aiogram.utils.exceptions import InvalidQueryID
from aiogram.types import InputTextMessageContent, InlineQueryResultArticle, InlineKeyboardMarkup, InlineKeyboardButton
from database import  insert_image, get_latest_image, add_employee_to_db, update_employee_birth_date, get_employee_birth_date, get_employees_with_birthday_today
from database import delete_employee_and_related_data,has_reported_today, add_report, get_employee_id_by_telegram_id, get_unreported_employees,  clear_schedule_and_plans_for_employee, get_sales_plan_for_employee, get_tariff_plan_for_employee, add_sales_plan_to_db, delete_schedule_from_db, unbind_telegram_user_from_employee, add_employee_to_db, is_holiday,  get_employees_working_on_date, get_all_employees_from_db, get_employee_name_by_telegram_id, bind_user_to_employee, add_schedule_to_db, get_employee_id_by_name,get_schedule_from_db,  get_employee_name_by_user_id
import re
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode
import asyncio
import logging
import aiocron
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import notes_db
from aiogram.utils.callback_data import CallbackData
import logging


class NameInputState(StatesGroup):
    name_input = State()

from aiogram.dispatcher.filters.state import State, StatesGroup

class SchedulePreferencesState(StatesGroup):
    preferences = State()


class ScheduleState(StatesGroup):
    name_input = State()
    birth_date_input = State()

class PlanState(StatesGroup):
    waiting_for_date = State()
    waiting_for_sales_plan = State()
    waiting_for_tariff_plan = State()

class ReportState(StatesGroup):
    proposals = State()
    sales = State()

class ScheduleSetting(StatesGroup):
    choosing_schedule = State()
    adding_template = State()

class DeleteEmployeeState(StatesGroup):
    waiting_for_employee_name = State()

class ScheduleTemplate(StatesGroup):
    waiting_for_time = State()

class AddShiftTemplate(StatesGroup):
    waiting_for_template = State()

class Schedule(StatesGroup):
    choosing_schedule = State()

class TicketForm(StatesGroup):
    title = State()  # Название тикета
    description = State()  # Описание
    email = State()  # Email

class TicketForm(StatesGroup):
    title = State()
    description = State()
    email = State()

class ScheduleTemplateState(StatesGroup):
    choosing_days = State()
    confirming = State()

import random

birthday_messages = [
    "🎉 С днем рождения, {name}! Желаем тебе всего самого лучшего! 🎂",
    "🎈 Поздравляем, {name}! Пусть этот день будет полон радости и счастья! 🎁",
    "🍰 Счастливого дня рождения, {name}! Наслаждайся каждым моментом! 🥳",
]


@aiocron.crontab('36 10 * * *')
async def send_birthday_notifications():
    logging.info("Запуск задачи отправки поздравлений с днем рождения")
    employees = get_employees_with_birthday_today()
    logging.info(f"Найдено сотрудников с днем рождения сегодня: {len(employees)}")
    if not employees:
        return  # Если сегодня нет дней рождения, ничего не делаем

    for name, username in employees:
        # Выбираем случайное сообщение из списка
        message = random.choice(birthday_messages).format(name=name)
        mention = f"@{username}" if username else name

        # Отправляем персонализированное сообщение в групповой чат
        await bot.send_message(chat_id=YOUR_GROUP_CHAT_ID, text=f"{mention}, {message}")



@aiocron.crontab('19 01 * * *')
async def send_notification():
    logging.info("Запуск задачи отправки уведомлений о графике работы")
    tomorrow = datetime.now() + timedelta(days=1)
    day = tomorrow.strftime('%d')  # Получаем число месяца для 'завтра'

    # Проверяем, является ли 'завтра' выходным днем
    if is_holiday(day):
        logging.info("Завтра выходной, уведомления не отправляются.")
        return

    # Получаем расписание на 'завтра'
    employees_working_tomorrow = get_employees_working_on_date(day)

    # Если работников нет, сообщаем об этом и завершаем функцию
    if not employees_working_tomorrow:
        logging.info("На завтра смены не запланированы.")
        return

    # Формируем текст уведомления
    message_text = f"Работают завтра ({tomorrow.strftime('%Y-%m-%d')}): \n"
    message_text += "— " * 10 + "\n"
    for employee in employees_working_tomorrow:
        name = employee.get('name')
        username = employee.get('username')
        start_time = employee['start_time']
        end_time = employee['end_time']
        mention = f"{name} (@{username})" if username else name
        message_text += f"{mention}:\n   ⌚ Время: с {start_time} до {end_time}\n"

    # Отправляем уведомление в групповой чат
    try:
        sent_message = await bot.send_message(chat_id=YOUR_GROUP_CHAT_ID, text=message_text)
        # Прикрепляем сообщение, если отправка прошла успешно
        await bot.pin_chat_message(chat_id=YOUR_GROUP_CHAT_ID, message_id=sent_message.message_id)
        logging.info("Уведомления успешно отправлены и прикреплены.")
    except Exception as e:
        logging.error(f"Ошибка при отправке уведомлений: {e}")


from logging.handlers import RotatingFileHandler
YOUR_GROUP_CHAT_ID = -4002403152
YOUR_ADMIN_ID = 525026259
ADMIN_ID = 525026259
API_TOKEN = '6307162615:AAFQ5-2dwmLMVxiPbEuxc3i6PFXTJOpGH68'
days_of_week = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"]
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='bot.log',
                    filemode='w', encoding='utf-8')


log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_handler = RotatingFileHandler('bot.log', mode='a', maxBytes=5*1024*1024, backupCount=2, encoding='utf-8', delay=0)
log_handler.setFormatter(log_formatter)
log_handler.setLevel(logging.DEBUG)

logger = logging.getLogger('aiogram')
logger.setLevel(logging.DEBUG)
logger.addHandler(log_handler)



from datetime import datetime, timedelta
pagination_cb = CallbackData('page', 'action', 'page_num')
note_cb = CallbackData('note', 'note_id')

PAGE_SIZE = 10  # Количество заметок на одной странице
import calendar


def get_days_with_dates():
    today = datetime.now()
    first_day_of_month = today.replace(day=1)
    days_in_month = calendar.monthrange(today.year, today.month)[1]

    days_with_dates = []
    for day in range(days_in_month):
        date = first_day_of_month + timedelta(days=day)
        day_abbr = days_translation[date.strftime("%a").upper()]
        days_with_dates.append((day_abbr, date.strftime("%d")))

    return days_with_dates


days_translation = {
    "MON": "ПН",
    "TUE": "ВТ",
    "WED": "СР",
    "THU": "ЧТ",
    "FRI": "ПТ",
    "SAT": "СБ",
    "SUN": "ВС"
}


import asyncio
import aiomysql
# Конфигурация подключения к базе данных
db_config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'Erik456_debul.ua21',
    'db': 'crm',
}

from datetime import datetime, timedelta




class TicketForm(StatesGroup):
    title = State()
    description = State()

# Функция для добавления новой заявки в базу данных
async def insert_new_ticket(telegram_user_id, title, description):
    client_id = 3
    project_id = 0
    ticket_type_id = 1
    created_by = 5  # ID пользователя, от имени которого создаются тикеты
    requested_by = 5
    status = 'new'
    assigned_to = 1
    creator_name = 'Ernest Worker'
    creator_email = 'tawerkarespro18@gmail.com'
    labels = ''
    task_id = 0
    merged_with_ticket_id = 0
    deleted = 0

    async with aiomysql.connect(**db_config, charset='utf8mb4', autocommit=True) as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                INSERT INTO rise_tickets 
                (client_id, project_id, ticket_type_id, title, created_by, requested_by, created_at, 
                 status, last_activity_at, assigned_to, creator_name, creator_email, labels, 
                 task_id, closed_at, merged_with_ticket_id, deleted) 
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s, NOW(), %s, %s, %s, %s, %s, %s, %s, %s)
                """, (client_id, project_id, ticket_type_id, title, created_by, requested_by,
                      status, assigned_to, creator_name, creator_email, labels, task_id,
                      '9999-12-31 23:59:59', merged_with_ticket_id, deleted))
            ticket_id = cur.lastrowid  # Получаем ID созданного тикета

            # Добавляем запись в telegram_ticket_link
            await cur.execute("""
                INSERT INTO telegram_ticket_link (telegram_user_id, ticket_id) 
                VALUES (%s, %s)
                """, (telegram_user_id, ticket_id))
            logging.info(f"Тикет {ticket_id} успешно создан и связан с пользователем Telegram {telegram_user_id}.")


# Обработчики команд и сообщений бота
@dp.message_handler(commands=['new_ticket'])
async def new_ticket(message: types.Message):
    await TicketForm.title.set()
    await message.answer("Введите название тикета:")

@dp.message_handler(state=TicketForm.title)
async def process_title(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['title'] = message.text
    await TicketForm.next()
    await message.answer("Введите описание тикета:")

@dp.message_handler(state=TicketForm.description)
async def process_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
    # Тут нужно получить telegram_user_id, например, так:
    telegram_user_id = message.from_user.id
    await insert_new_ticket(telegram_user_id, data['title'], data['description'])
    await state.finish()
    await message.answer("Ваш тикет успешно создан и добавлен в базу данных!")




# Переменная для отслеживания последнего уведомленного комментария
last_sent_comment_id = {}

async def fetch_new_comments():
    logging.info("Проверка новых комментариев от админа...")
    async with aiomysql.connect(**db_config) as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("""
                SELECT rtc.id, rtc.description, rtc.ticket_id, ttl.telegram_user_id
                FROM rise_ticket_comments AS rtc
                JOIN rise_tickets AS rt ON rtc.ticket_id = rt.id
                JOIN telegram_ticket_link AS ttl ON rt.id = ttl.ticket_id
                WHERE rtc.created_by = 1 AND rtc.deleted = 0 AND rt.status != 'closed'
                ORDER BY rtc.id DESC
            """)
            comments = await cur.fetchall()
            for comment in comments:
                ticket_id = comment['ticket_id']
                if ticket_id not in last_sent_comment_id or comment['id'] > last_sent_comment_id[ticket_id]:
                    chat_id = comment['telegram_user_id']
                    if chat_id:
                        message = comment['description'].replace('<p>', '').replace('</p>', '\n').replace('<br>', '\n').strip()
                        await bot.send_message(chat_id, f"Новый комментарий к заявке '{ticket_id}': {message}")
                        last_sent_comment_id[ticket_id] = comment['id']
                    else:
                        logging.warning(f"Chat ID для пользователя с Telegram ID {comment['telegram_user_id']} не найден.")





@dp.message_handler(commands=['add_comment'])
async def add_comment(message: types.Message):
    args = message.get_args().split(maxsplit=1)
    if len(args) < 2:
        await message.reply("Используйте команду в формате: /add_comment <id_заявки> <комментарий>")
        return

    ticket_id, comment_text = args[0], args[1]
    try:
        ticket_id = int(ticket_id)
    except ValueError:
        await message.reply("ID заявки должен быть числом.")
        return

    sql_query = """
        INSERT INTO rise_ticket_comments (created_by, ticket_id, description, created_at, deleted, files, is_note)
        VALUES (%s, %s, %s, NOW(), 0, 'a:0:{}', 0)
    """
    sql_data = (5, ticket_id, comment_text)

    try:
        async with aiomysql.connect(**db_config, cursorclass=aiomysql.DictCursor) as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT status FROM rise_tickets WHERE id = %s", (ticket_id,))
                ticket = await cur.fetchone()
                if ticket and ticket['status'] != 'closed':
                    await cur.execute(sql_query, sql_data)
                    await conn.commit()
                    await message.reply("Ваш комментарий добавлен к заявке.")
                else:
                    await message.reply("Заявка закрыта или не найдена. Добавление комментария невозможно.")
    except Exception as e:
        logging.error(f"Ошибка при выполнении SQL-запроса: {e}")
        await message.reply("Произошла ошибка при попытке добавить комментарий. Пожалуйста, попробуйте позже.")








notified_closed_tickets = set()
async def check_ticket_closed():
    logging.info("Проверка статуса заявок...")
    async with aiomysql.connect(**db_config) as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("""
                SELECT rt.id, ttl.telegram_user_id
                FROM rise_tickets rt
                JOIN telegram_ticket_link ttl ON rt.id = ttl.ticket_id
                WHERE rt.status = 'closed'
            """)
            closed_tickets = await cur.fetchall()
            for ticket in closed_tickets:
                ticket_id = ticket['id']
                if ticket_id not in notified_closed_tickets:
                    telegram_user_id = ticket['telegram_user_id']
                    # Отправляем уведомление пользователю Telegram о закрытии тикета
                    await bot.send_message(telegram_user_id, f"Заявка {ticket_id} была закрыта.")
                    logging.info(f"Пользователь {telegram_user_id} уведомлен о закрытии заявки {ticket_id}.")

                    # Удаляем связь из telegram_ticket_link
                    logging.info(f"Попытка удалить связь тикета {ticket_id} из telegram_ticket_link...")
                    await cur.execute("""
                        DELETE FROM telegram_ticket_link
                        WHERE ticket_id = %s
                    """, (ticket_id,))
                    await conn.commit()
                    logging.info(f"Связь тикета {ticket_id} удалена из telegram_ticket_link.")

                    # Добавляем идентификатор заявки в множество уведомленных
                    notified_closed_tickets.add(ticket_id)


import requests

def publish_telegraph_article(title, author_name, content, author_url=None):
    create_article_url = 'https://api.telegra.ph/createPage'
    token = 'YourTelegraphAccessToken'
    payload = {
        'access_token': '037bdafc612f5a8904da52815c4f1ff87504e692bd1c5ced0814c1b94281',
        'title': title,
        'content': content,
        'author_name': 'Kolomoyets',
        'author_url': 'https://t.me/yarmitt'
    }
    response = requests.post(create_article_url, json=payload)
    return response.json()


import json


class ArticleForm(StatesGroup):
    waiting_for_title = State()  # Состояние ожидания названия статьи
    waiting_for_content = State()  # Состояние ожидания содержимого статьи

@dp.message_handler(commands=['savenote'], state='*')
async def start_saving_article(message: Message, state: FSMContext):
    await ArticleForm.waiting_for_title.set()
    await message.reply("Пожалуйста, введите название статьи:")

@dp.message_handler(state=ArticleForm.waiting_for_title)
async def article_title_received(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['title'] = message.text
    await ArticleForm.next()
    await message.reply("Теперь отправьте содержимое статьи:")

@dp.message_handler(state=ArticleForm.waiting_for_content)
async def article_content_received(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['content'] = message.text
        title = data['title']
        content = json.dumps([{"tag": "p", "children": [data['content']]}])
        result = publish_telegraph_article(title, "Your Author Name", content)

        if result.get('ok'):
            article_url = result['result']['url']
            # Здесь сохраняем название, URL и содержимое статьи в базу данных
            notes_db.save_article(message.from_user.id, title, article_url, data['content'])
            await message.reply(f"Статья сохранена. Просмотрите её здесь: {article_url}")
        else:
            await message.reply("Не удалось создать статью.")
    await state.finish()

@dp.message_handler(commands=['deletenote'])
async def delete_note_handler(message: types.Message):
    # Разбираем команду на части и извлекаем идентификатор статьи
    parts = message.text.split(maxsplit=1)
    if len(parts) != 2 or not parts[1].isdigit():
        await message.reply("Пожалуйста, укажите идентификатор статьи для удаления. Например: /deletenote 123")
        return

    article_id = int(parts[1])
    # Теперь вызываем функцию удаления
    try:
        notes_db.delete_article_by_id(article_id)
        await message.reply(f"Статья с идентификатором {article_id} была успешно удалена.")
    except Exception as e:
        await message.reply(f"Произошла ошибка при удалении статьи: {e}")


@dp.message_handler(commands=['getnotes'])
async def get_notes_handler(message: types.Message, page_num: int = 1):
    articles, total_pages = notes_db.get_articles_page(page_num, 5)

    keyboard = InlineKeyboardMarkup(row_width=2)
    for article in articles:
        article_id, article_title, article_url = article[0], article[2], article[3]
        button_text = f"{article_title} (ID: {article_id})"
        keyboard.add(InlineKeyboardButton(text=button_text, url=article_url))

    pagination_buttons = []
    if page_num > 1:
        pagination_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"page_{page_num-1}"))
    if page_num < total_pages:
        pagination_buttons.append(InlineKeyboardButton("Вперед ➡️", callback_data=f"page_{page_num+1}"))
    keyboard.row(*pagination_buttons)

    await message.reply("Выберите статью:", reply_markup=keyboard)




@dp.callback_query_handler(note_cb.filter())
async def query_note(callback_query: types.CallbackQuery, callback_data: dict):
    note_id = int(callback_data['note_id'])
    note = notes_db.get_note_by_id(note_id)
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, f"Заметка:\n{note[2]}")


@dp.callback_query_handler(pagination_cb.filter(action=['prev', 'next']))
async def query_page(callback_query: types.CallbackQuery, callback_data: dict):
    await get_notes_handler(callback_query.message, int(callback_data['page_num']))

@dp.message_handler(commands=['search'])
async def search_articles_handler(message: types.Message):
    query = message.get_args()
    page_num = 1
    articles, total_pages = notes_db.search_articles(query, page_num, PAGE_SIZE)

    if not articles:
        await message.reply("По вашему запросу статьи не найдены.")
        return

    keyboard = InlineKeyboardMarkup(row_width=1)
    for article in articles:
        title_preview = article[2][:30] + '...' if len(article[2]) > 30 else article[2]
        keyboard.add(InlineKeyboardButton(text=title_preview, url=article[3]))

    pagination_buttons = []
    if page_num > 1:
        pagination_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"search_prev_{page_num-1}_{query}"))
    if page_num < total_pages:
        pagination_buttons.append(InlineKeyboardButton("Вперёд ➡️", callback_data=f"search_next_{page_num+1}_{query}"))
    if pagination_buttons:
        keyboard.row(*pagination_buttons)

    await message.reply("Найденные статьи:", reply_markup=keyboard)





@dp.message_handler(lambda message: message.from_user.id == ADMIN_ID, commands=['admin'])
async def send_test(message: types.Message):
    await message.answer("Вот мои команды:\n\n"
                         "/start - начало работы\n\n"
                         "/upload_schedule - загрузка графика работы\n\n"
                         "/view_schedule - просмотр текущего графика работы\n\n"
                         "/remind (today/tomorrow)- Напоминалка на сегодня и на завтра\n\n"
                         "/add_employee - Добавить раба\n\n"
                         "/delete_employee - delete раб\n\n"
                         "/choose_employee - список рабов\n\n"
                         "/add_shift_template - Добавить шаблон времени для рабов\n\n"
                         "/deletenote - удалить статью(нужно указать айди, найти через команду /getnotes)")

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("Hi, я твой помощник. Вот мои команды:\n\n"
                         "/add_comment - добавить комент к заявке\n\n"
                         "/new_ticket - заявка разрабу\n\n"
                         "/search - поиск статьи\n\n"
                         "/getnotes - отобразить статьи\n\n"
                         "/savenote - сохранить заметку в ввиде статьи\n\n"
                         "/view_schedule - просмотр текущего графика работы\n\n"
                         "/unbind - Удалить привязку акк ТГ и Раба\n\n"
                         "/schedule - Привязка ТГ акк к своим инициалам + посмотри свой график\n\n"
                         "/set_preferences - Отправить пожелание по времени работы")


shift_options = {

}



@dp.message_handler(lambda message: message.from_user.id == ADMIN_ID, commands=['remind'])
async def remind_employees(message: types.Message):
    parts = message.text.split()
    if len(parts) < 2:
        await message.reply("Пожалуйста, укажите 'today' или 'tomorrow' после команды /remind")
        return

    command = parts[1]
    if command == "today":
        day = datetime.now().strftime('%d')
        remind_date_str = datetime.now().strftime('%Y-%m-%d')
    elif command == "tomorrow":
        day = (datetime.now() + timedelta(days=1)).strftime('%d')
        remind_date_str = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')  # Полная дата для вывода

    employees = get_employees_working_on_date(day)
    reminders = []

    for employee in employees:
        telegram_id = employee['telegram_id']
        reminder_text = (
            f"🔔 Напоминание для @{employee['username'] or 'None'} ({employee['name']}) на {remind_date_str} 🔔\n"
            "────────────────────\n"
            f"⌚ Время: с {employee['start_time']} до {employee['end_time']}\n"
            "\n────────────────────")

        reminders.append(reminder_text)
        if telegram_id:
            await bot.send_message(telegram_id, reminder_text)

    all_reminders_text = "\n\n".join(reminders)
    if all_reminders_text:
        group_chat_id = YOUR_GROUP_CHAT_ID
        await bot.send_message(group_chat_id, all_reminders_text)
    else:
        await message.reply("На запрошенную дату смены не запланированы.")

    await message.reply(f"Напоминания на {command} отправлены!")



from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


report_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
report_button = KeyboardButton("Подать отчет")
report_keyboard.add(report_button)

@dp.message_handler(lambda message: message.text == "Подать отчет")
async def report_start(message: types.Message):
    await message.answer("Пожалуйста, введите количество выполненных предложений:", reply_markup=types.ReplyKeyboardRemove())
    await ReportState.proposals.set()

@dp.message_handler(lambda message: message.text.isdigit(), state=ReportState.proposals)
async def process_proposals(message: types.Message, state: FSMContext):
    proposals = int(message.text)
    await state.update_data(proposals=proposals)
    data = await state.get_data()  # Add this line
    print(f"Data after saving: {data}")  # Add this line
    await message.answer("Теперь введите количество продаж:")
    await ReportState.sales.set()


@dp.message_handler(lambda message: message.text.isdigit(), state=ReportState.sales)
async def process_sales(message: types.Message, state: FSMContext):
    data = await state.get_data()
    proposals = data.get("proposals")
    sales = int(message.text)

    print(f"Data before inserting: {data}")

    if proposals is None:
        print("Error: Proposals is None!")
        await message.answer("Ошибка: значение предложений отсутствует.")
        await state.finish()
        return

    user_id = message.from_user.id
    employee_id = get_employee_id_by_telegram_id(user_id)

    if not has_reported_today(employee_id):
        add_report(employee_id, proposals, sales)
        await message.answer(f"Вы подали отчет! Предложений: {proposals}, Продаж: {sales}")
    else:
        await message.answer("Вы уже подали отчет сегодня.")

    await state.finish()




@dp.message_handler(lambda message: message.text.startswith('/add_employee'), user_id=YOUR_ADMIN_ID)
async def add_employee(message: types.Message):
    print("Received command: /add_employee")
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Name was not provided. Provide the name after the command.")
        return
    employee_name = ' '.join(parts[1:])
    print(f"Adding employee: {employee_name}")
    add_employee_to_db(employee_name)
    await message.answer(f"Сотрудник {employee_name} успешно добавлен!")





@dp.message_handler(commands=['unbind'])
async def unbind_user(message: types.Message):
    user_id = message.from_user.id
    employee_name = get_employee_name_by_telegram_id(user_id)

    if not employee_name:
        await message.answer("Ваш аккаунт не был привязан к имени сотрудника.")
        return

    unbind_telegram_user_from_employee(user_id)
    await message.answer(f"Привязка вашего аккаунта к имени {employee_name} была удалена.")


@dp.message_handler(commands=['delete_employee'])
async def delete_employee_command(message: Message):
    if message.from_user.id == YOUR_ADMIN_ID:
        await message.answer("Введите имя сотрудника, которого хотите удалить:")
        await DeleteEmployeeState.waiting_for_employee_name.set()
    else:
        await message.answer("У вас нет прав на выполнение этой команды.")

@dp.message_handler(state=DeleteEmployeeState.waiting_for_employee_name)
async def get_employee_name_to_delete(message: Message, state: FSMContext):
    employee_name = message.text
    delete_employee_and_related_data(employee_name)
    await message.answer(f"Сотрудник {employee_name} и все связанные с ним данные удалены.")
    await state.finish()  # Завершение состояния


@dp.callback_query_handler(lambda call: call.data.startswith('employee'))
async def handle_employee_choice(call: types.CallbackQuery):
    if call.message is None:
        await call.answer("Не могу обработать ваш запрос. Пожалуйста, попробуйте еще раз.")
        return

    _, employee_name = call.data.split(":")
    employee_id = get_employee_id_by_name(employee_name)
    days_with_dates = get_days_with_dates()
    existing_schedule = get_schedule_from_db(employee_name)
    scheduled_days = [day.lstrip('0') for day, _, _ in existing_schedule]

    markup = InlineKeyboardMarkup()
    week_row = []
    for day_str, day_num in days_with_dates:
        button_text = f"{day_str} ({day_num})"
        if day_num.lstrip('0') in scheduled_days:
            button_text += " 📌"
        week_row.append(InlineKeyboardButton(button_text, callback_data=f"day:{employee_name}:{day_num}"))
        if len(week_row) == 3:
            markup.row(*week_row)
            week_row = []
    if week_row:
        markup.row(*week_row)

    markup.add(InlineKeyboardButton("Очистить график и планы", callback_data=f"clear_schedule:{employee_name}"))
    markup.add(InlineKeyboardButton("Завершить", callback_data=f"finish:{employee_name}"))

    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Выберите день недели для {employee_name}:",
        reply_markup=markup
    )



@dp.callback_query_handler(lambda call: call.data.startswith('clear_schedule:'))
async def handle_clear_schedule(call: types.CallbackQuery):
    _, employee_name = call.data.split(":")
    employee_id = get_employee_id_by_name(employee_name)
    clear_schedule_and_plans_for_employee(employee_id)
    await call.answer(f"График и планы для {employee_name} были очищены.")


@dp.callback_query_handler(lambda call: call.data.startswith('day'))
async def handle_day_choice(call: types.CallbackQuery):
    _, employee_name, day = call.data.split(":")
    markup = InlineKeyboardMarkup(row_width=1)

    # Кнопки для установки времени, выходного и плана
    markup.add(InlineKeyboardButton("Установить время", callback_data=f"set_time:{employee_name}:{day}"))
    markup.add(InlineKeyboardButton("Назад", callback_data=f"employee:{employee_name}"))

    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text=f"Выберите действие для {employee_name} в {day}:",
                                reply_markup=markup)


@dp.callback_query_handler(lambda call: call.data.startswith('set_time'))
async def choose_time_for_schedule(call: types.CallbackQuery):
    _, employee_name, day = call.data.split(":")
    markup = InlineKeyboardMarkup(row_width=1)

    # Получение и сортировка пользовательских смен из базы данных
    shift_templates = database.get_shift_templates()
    shift_templates = sorted(shift_templates, key=lambda x: x[0] or '')

    # Добавление смен
    for i, (start, end) in enumerate(shift_templates, start=1):
        button_text = f"Смена {i} ({start or '—'} - {end or '—'})"
        button = InlineKeyboardButton(button_text,
                                      callback_data=f"time_selected;{employee_name};{day};{start or 'None'};{end or 'None'}")
        markup.add(button)

    # Добавляем кнопку "Назад"
    markup.add(InlineKeyboardButton("Назад", callback_data=f"day:{employee_name}:{day}"))

    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text=f"Выберите время для {employee_name} на {day}:",
                                reply_markup=markup)




@dp.callback_query_handler(lambda call: call.data.startswith('time_selected'))
async def set_time_for_schedule(call: types.CallbackQuery):
    # Разбиваем данные по символу ";"
    data_parts = call.data.split(";")

    if len(data_parts) != 5:
        await bot.send_message(call.message.chat.id, "Ошибка: Неверный формат данных.")
        return

    _, employee_name, day, start_time, end_time = data_parts

    # Если выбран "Выходной", то время будет None
    if start_time == "None":
        start_time = None
    if end_time == "None":
        end_time = None

    # Получаем ID сотрудника по имени
    employee_id = get_employee_id_by_name(employee_name)

    if employee_id is not None:
        # Добавляем выбранное время в базу данных
        add_schedule_to_db(employee_id, day, start_time, end_time)
        await bot.send_message(call.message.chat.id,
                               f"Установлено время работы для {employee_name} на {day}: с {start_time or '—'} до {end_time or '—'}")
        call.data = f"employee:{employee_name}"
        await handle_employee_choice(call)

    else:
        await bot.send_message(call.message.chat.id, f"Ошибка: Не удалось найти ID сотрудника для {employee_name}")




@dp.callback_query_handler(lambda call: call.data.startswith('set_plan'))
async def handle_set_plan(call: types.CallbackQuery, state: FSMContext):
    _, employee_name, day = call.data.split(":")
    await PlanState.waiting_for_sales_plan.set()  # переход к состоянию ожидания плана продаж
    await state.update_data(employee_name=employee_name, plan_date=day)
    await call.message.answer(f"Введите план продаж для {employee_name} на {day}:")


@dp.message_handler(lambda message: message.text.isdigit(), state=PlanState.waiting_for_sales_plan)
async def handle_sales_plan(message: types.Message, state: FSMContext):
    sales_plan = int(message.text)
    await state.update_data(sales_plan=sales_plan)
    await PlanState.waiting_for_tariff_plan.set()
    await message.answer("Введите план предложений тарифов:")

@dp.message_handler(lambda message: message.text.isdigit(), state=PlanState.waiting_for_tariff_plan)
async def handle_tariff_plan(message: types.Message, state: FSMContext):
    data = await state.get_data()
    sales_plan = data.get("sales_plan")
    tariff_plan = int(message.text)
    employee_name = data.get("employee_name")
    employee_id = get_employee_id_by_name(employee_name)
    day = data.get("plan_date") # извлекаем дату из FSMContext
    add_sales_plan_to_db(employee_id, day, sales_plan, tariff_plan)
    await message.answer("Планы успешно добавлены!")
    await state.finish()

    # Возвращаемся к выбору дня недели
    call = types.CallbackQuery(data=f"employee:{employee_name}")
    await handle_employee_choice(call)

@dp.callback_query_handler(lambda call: call.data.startswith('finish'))
async def handle_finish(call: types.CallbackQuery):
    _, employee_name = call.data.split(":")
    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text=f"График для {employee_name} сохранён!")
    await choose_employee(call.message)

@dp.message_handler(lambda message: message.text.startswith('/choose_employee'), user_id=YOUR_ADMIN_ID)
async def choose_employee(message: types.Message):
    employees = get_all_employees_from_db()
    if not employees:
        await message.answer("Список сотрудников пуст.")
        return
    markup = InlineKeyboardMarkup(row_width=1)
    for employee in employees:
        button = InlineKeyboardButton(employee, callback_data=f"employee:{employee}")
        markup.add(button)
    await message.answer("Выберите сотрудника:", reply_markup=markup)


@dp.message_handler(commands=['upload_schedule'])
async def upload_schedule(message: types.Message):
    await message.answer("Пожалуйста, загрузите изображение графика работы на следующую неделю.")

@dp.message_handler(content_types=types.ContentType.PHOTO)
async def handle_docs_photo(message: types.Message):
    file_id = message.photo[-1].file_id
    upload_date = datetime.now()

    insert_image(file_id, upload_date)
    await message.reply("График работы успешно загружен!")



@dp.message_handler(commands=['view_schedule'])
async def view_schedule(message: types.Message):
    file_id = get_latest_image()
    if file_id:
        await message.reply_photo(file_id[0])
    else:
        await message.answer("График работы на следующую неделю пока не был загружен.")




# Функция для проверки корректности даты
def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

# Обработчик для состояния birth_date_input
@dp.message_handler(state=ScheduleState.birth_date_input)
async def save_birth_date(message: types.Message, state: FSMContext):
    birth_date = message.text

    # Проверка корректности даты
    if not is_valid_date(birth_date):
        await message.reply("Пожалуйста, введите дату в правильном формате (ГГГГ-ММ-ДД).")
        return

    # Получаем имя сотрудника
    user_id = message.from_user.id
    employee_name = get_employee_name_by_telegram_id(user_id)

    # Обновляем дату рождения в базе данных
    update_employee_birth_date(employee_name, birth_date)

    await message.reply(f"Для {employee_name} установлена дата рождения: {birth_date}")
    await state.finish()

@dp.message_handler(commands=['schedule'])
async def show_user_schedule(message: types.Message):
    user_id = message.from_user.id
    employee_name = get_employee_name_by_telegram_id(user_id)

    if not employee_name:
        await message.answer("Пожалуйста, укажите ваше имя и фамилию на английском языке:")
        await NameInputState.name_input.set()
        return

    # Проверка наличия даты рождения
    birth_date = get_employee_birth_date(employee_name)
    if not birth_date:
        await message.answer("Введите дату рождения в формате ГГГГ-ММ-ДД:")
        await ScheduleState.birth_date_input.set()
        return

        # Показ графика работы, если дата рождения уже установлена
    schedule = get_schedule_from_db(employee_name)
    if not schedule:
        await message.answer(f"Для {employee_name} график работы пока не установлен.")
        return

    days_with_dates = get_days_with_dates()
    response = f"График работы для {employee_name}:\n"
    for work_day, start_time, end_time in schedule:
        # Найдем соответствующий день недели в списке days_with_dates
        day_date = next((d for d, day in days_with_dates if day == work_day), None)
        response += f"{work_day} ({day_date}): с {start_time} до {end_time}\n"

    await message.answer(response)

@dp.message_handler(state=NameInputState.name_input)
async def handle_name_input(message: types.Message, state: FSMContext):
    print("handle_name_input triggered")
    user_id = message.from_user.id
    username = message.from_user.username
    employee_name = message.text

    employees_from_db = get_all_employees_from_db()
    print(f"Employees from DB: {employees_from_db}")

    for name in employees_from_db:
        print(f"Comparing '{employee_name}' with '{name}'")
        if name.lower() == employee_name.lower():
            print("Names are identical!")
            bind_user_to_employee(user_id, employee_name, username)
            await message.answer(f"Ваше имя и фамилия ({employee_name}) привязаны к вашему аккаунту. Теперь вы можете использовать команду /schedule, чтобы узнать ваш график.")
            await state.finish()
            return

    await message.answer("Не удалось найти сотрудника с таким именем. Попробуйте снова.")


from datetime import datetime, timedelta, time
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)



from aiogram.dispatcher.filters import Command
import database


@dp.message_handler(Command('add_shift_template'), state='*')
async def start_adding_shift_template(message: types.Message):
    await ScheduleSetting.adding_template.set()
    await message.answer("Введите время для нового шаблона смены в формате 'HH:MM-HH:MM'")


@dp.message_handler(state=ScheduleSetting.adding_template)
async def add_shift_template(message: types.Message, state: FSMContext):
    try:
        start_time, end_time = message.text.split('-')
        database.add_shift_template(start_time, end_time)
        await message.answer("Шаблон смены успешно добавлен!")
    except Exception as e:
        await message.answer("Произошла ошибка. Пожалуйста, проверьте формат ввода.")
        print(e)
    finally:
        await state.finish()



@dp.message_handler(Command('set_schedule'), state='*')
async def start_setting_schedule(message: types.Message):
    await ScheduleSetting.choosing_schedule.set()
    await message.answer("Выберите смену:", reply_markup=await get_schedule_keyboard())


async def get_schedule_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)

    # Получение смен из базы данных
    templates = database.get_shift_templates()
    for template in templates:
        shift_name, start, end = template[1], template[2], template[3]
        button_text = f"{shift_name} ({start or '—'} - {end or '—'})"
        button = InlineKeyboardButton(button_text, callback_data=f"schedule:{shift_name}")
        markup.add(button)

    return markup

@dp.message_handler(Command('set_preferences'), state='*')
async def start_setting_preferences(message: types.Message):
    await SchedulePreferencesState.preferences.set()
    await message.answer("Введите пожелания по графику работы в формате 'День (Число): с HH:MM до HH:MM', например 'ПН (06): с 13:00 до 21:00'. Для завершения ввода введите /done.")

@dp.message_handler(state=SchedulePreferencesState.preferences)
async def set_preferences(message: types.Message, state: FSMContext):
    preferences_text = message.text
    user_id = message.from_user.id

    async with state.proxy() as data:
        if 'preferences' not in data:
            data['preferences'] = []

        if message.text.lower() == '/done':
            await message.answer("Ваши пожелания по графику работы были отправлены администратору для подтверждения.")
            admin_user_id = '525026259'
            preferences_message = "\n".join(data['preferences'])
            await bot.send_message(admin_user_id, f"Пожелания графика работы для пользователя {user_id}:\n{preferences_message}")


            await state.finish()
        else:
            data['preferences'].append(preferences_text)
            await message.answer("Пожелание сохранено. Введите следующее пожелание или введите /done для завершения ввода.")


async def periodic_task(interval, task_func, *args):
    while True:
        try:
            await task_func(*args)  # Выполнение вашей функции
        except Exception as e:
            logging.error(f"Ошибка при выполнении задачи {task_func.__name__}: {e}")
        await asyncio.sleep(interval)  # Ожидание до следующего выполнения


async def on_startup(dp):
    await bot.send_message(ADMIN_ID, "Bot has been started")
    # Запуск периодической задачи проверки новых комментариев каждые 10 секунд
    asyncio.create_task(periodic_task(10, fetch_new_comments))
    # Запуск периодической задачи проверки закрытых заявок каждые 10 секунд
    asyncio.create_task(periodic_task(10, check_ticket_closed))



if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, on_startup=on_startup)