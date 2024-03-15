import sqlite3

def db_connect():
    return sqlite3.connect('db.db')


def delete_article_by_id(article_id):
    connection = db_connect()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM articles WHERE id = ?", (article_id,))
    connection.commit()
    connection.close()



def save_article(user_id, title, url, content=None):
    connection = db_connect()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO articles (user_id, title, url, content) VALUES (?, ?, ?, ?)", (user_id, title, url, content))  # Добавьте content в запрос, если он используется
    connection.commit()
    connection.close()


def get_articles_page(page_num, page_size):
    connection = db_connect()
    cursor = connection.cursor()
    offset = (page_num - 1) * page_size
    cursor.execute("SELECT id, user_id, title, url FROM articles LIMIT ? OFFSET ?", (page_size, offset))
    articles = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM articles")
    total_count = cursor.fetchone()[0]
    total_pages = (total_count + page_size - 1) // page_size

    connection.close()
    return articles, total_pages


def get_article_by_id(article_id):
    connection = db_connect()
    cursor = connection.cursor()
    cursor.execute("SELECT id, user_id, title, url FROM articles WHERE id = ?", (article_id,))
    article = cursor.fetchone()
    connection.close()
    return article


def search_articles(query, page_num, page_size):
    connection = db_connect()
    cursor = connection.cursor()

    # Модифицируем SQL запрос для поиска по заголовкам статей
    sql_query = "SELECT id, user_id, title, url FROM articles WHERE title LIKE ? LIMIT ? OFFSET ?"

    # Рассчитываем смещение на основе номера страницы и размера страницы
    offset = (page_num - 1) * page_size
    cursor.execute(sql_query, ('%' + query + '%', page_size, offset))
    articles = cursor.fetchall()

    # Вычисляем общее количество статей удовлетворяющих запросу для пагинации
    cursor.execute("SELECT COUNT(*) FROM articles WHERE title LIKE ?", ('%' + query + '%',))
    total_count = cursor.fetchone()[0]
    total_pages = (total_count + page_size - 1) // page_size

    connection.close()
    return articles, total_pages


def save_note(user_id, text, message_id=None):
    connection = db_connect()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO notes (user_id, text, message_id) VALUES (?, ?, ?)", (user_id, text, message_id))
    connection.commit()
    connection.close()

def get_notes_page(page_num, page_size):
    connection = db_connect()
    cursor = connection.cursor()
    offset = (page_num - 1) * page_size
    cursor.execute("SELECT id, user_id, text FROM notes LIMIT ? OFFSET ?", (page_size, offset))
    notes = cursor.fetchall()
    connection.close()
    return notes

def get_total_pages(page_size):
    connection = db_connect()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM notes")
    total_notes = cursor.fetchone()[0]
    total_pages = (total_notes + page_size - 1) // page_size
    connection.close()
    return total_pages

def get_note_by_id(note_id):
    connection = db_connect()
    cursor = connection.cursor()
    cursor.execute("SELECT id, user_id, text FROM notes WHERE id = ?", (note_id,))
    note = cursor.fetchone()
    connection.close()
    return note
