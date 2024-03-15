import requests

def create_telegraph_account(short_name, author_name, author_url=None):
    url = 'https://api.telegra.ph/createAccount'
    payload = {
        'short_name': '',
        'author_name': '',
        'author_url': ''
    }
    response = requests.post(url, json=payload)
    return response.json()

# Вызов функции для создания аккаунта
account_info = create_telegraph_account('', '', '')
print(account_info)
C:\Users\tawer\AppData\Local\Programs\Python\Python310\python.exe C:/Users/tawer/PycharmProjects/botwork/1.py
{'ok': True, 'result': {'short_name': 'Ernestoss', 'author_name': 'Kolomoyets', 'author_url': 'https://t.me/yarmitt', 'access_token': '037bdafc612f5a8904da52815c4f1ff87504e692bd1c5ced0814c1b94281', 'auth_url': 'https://edit.telegra.ph/auth/Yi2HnHB5LPDM9TKyFGJlTIzuEuUWIWHEeJlCqWF9Jh'}}

Process finished with exit code 0
