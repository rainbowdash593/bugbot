import re
import logging
import requests
from os import environ
from app.utils.jira import Jira

class Bot:
    def __init__(self, bot_id, api_key):
        self.bot_id = bot_id
        self.api_key = api_key
        self.url = 'https://api.telegram.org/bot{bot_id}:{api_key}'.format(bot_id=bot_id, api_key=api_key)

    def send_message(self, chat_id, text):
        resp = None
        try:
            req = requests.get(self.url + '/sendMessage?chat_id={chat_id}&text={text}'.format(chat_id=chat_id,
                                                                                              text=text))
            resp = req.json()
        except Exception as e:
            logging.error('Failed to send message: {e}'.format(e=e))
        return resp

class Actions:
    def __init__(self, text, chat_id):
        self.text = text
        self.chat_id = chat_id
        self.command = text.split(' ')[0] if len(text.split(' ')) else None
        self.tagged_members = re.findall(r'\@\w+', self.text)
        self.bot = Bot(environ.get('TELEGRAM_BOT_ID'), environ.get('TELEGRAM_API_KEY'))

    def is_command_exists(self):
        return True if self.command else False

    def get_title(self):
        title = self.text.replace(self.command, '')
        for member in self.tagged_members:
            title.replace(member, '')
        return title.strip()

    def create_bug(self):
        logging.error(self.get_title())
        if len(self.tagged_members):
            jira = Jira()
            for member in self.tagged_members:
                jira.create_issue(self.get_title(), member)
            self.bot.send_message(self.chat_id, 'Создаю для {members} карточку О_о'.format(members=', '.join(self.tagged_members)))

    def dispatch(self):
        if self.command == '/баг' or '/bug':
            self.create_bug()
