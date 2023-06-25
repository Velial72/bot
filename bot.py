import os
import sqlite3

from datetime import datetime
import time
# from main_functions import show_timeline
import telebot
from telebot import types
from dotenv import load_dotenv
from pathlib import Path
from django.core.management.base import BaseCommand
# from django.conf import settings
# from meetup.bot.models import User, Speaker, Message

load_dotenv()
token = '6125022357:AAHc-FiPd5qsIyHhKaAiTKIft-1h1Jq34HU'
bot = telebot.TeleBot(token)
path = Path("meetup", "db.meetup")
conn = sqlite3.connect(path, check_same_thread=False)
cursor = conn.cursor()
params = []
questions = []
author_of_quastion = []
speaker_name = ''


def now_time(): # выдает текущий час
    current_time = datetime.now().hour
    return current_time


def get_speakers_list(): #выводит список спикеров
    cursor.execute(f"SELECT user_id FROM bot_speaker")
    speakers_name = cursor.fetchall()
    print(10)
    print(speakers_name)
    return speakers_name


def get_timeline(): # выдает боту график мероприятия
    cursor.execute("SELECT * FROM bot_speaker;")
    return cursor.fetchall()


def check_meet(speaker_name): #проверяет задержку выступления
    cursor.execute(f"SELECT delay FROM bot_speaker WHERE user_id == '{speaker_name}'")
    answer = cursor.fetchone()[0]
    print(type(answer))
    print(answer)
    return answer


def get_name(message): # получить данные спикера
    speaker_name = message.from_user.id
    print(speaker_name)
    check_meet(speaker_name)


def get_name_visitor(message): # получить данные пользователя
    visitor_name = message.from_user.first_name
    visitor_id = message.from_user.id
    print((visitor_id))
    params.append(visitor_id)
    params.append(visitor_name)
    check_user(visitor_id)


def check_user(tg_id): # проверяет записан ли пользователь
    cursor.execute(f"SELECT tg_id FROM bot_user WHERE tg_id == {tg_id}")
    data = cursor.fetchone()
    if data is None:
        add_user(tg_id=params[0], name=params[1])


def find_speaker(): # находит имя спикера по времени
    cursor.execute(f"SELECT user_id FROM bot_speaker WHERE start_date == '{now_time()}:00';")
    name_of_speaker = cursor.fetchone()
    return name_of_speaker[0]


def get_question(message): # получает вопрос от пользователя
    question = message.text
    name_visitor = message.from_user.username
    questions.append(question)
    author_of_quastion.append(name_visitor)
    print(questions)
    send_question(guest=name_visitor, speaker=find_speaker(), message=questions)


def add_user(tg_id: str, name: str): # добавить пользователя в БД
    cursor.execute('INSERT INTO bot_user(tg_id, name) VALUES (?,?)',
                   (params[0], params[1]))
    conn.commit()


def get_my_questions(): # выводит вопросы спикеру

    print(find_speaker())
    cursor.execute(f"SELECT * FROM bot_message WHERE speaker_id == '{find_speaker()}';")
    return cursor.fetchall()


def send_question(guest: str, speaker: str, message: str): # добавляет вопрос в БД
    cursor.execute('INSERT INTO bot_message(guest_id, speaker_id, message) VALUES (?,?,?)',
                   (author_of_quastion[-1], find_speaker(), questions[-1]))
    conn.commit()


@bot.message_handler(content_types=['text']) # Пришли сообщение чтобы начать
def start(message):
    if message.from_user.username == 'AbRamS040':
        markup = types.InlineKeyboardMarkup(row_width=1)
        timeline = types.InlineKeyboardButton('График выступлений', callback_data='timeline2')
        markup.add(timeline)
        bot.send_message(message.chat.id, '\nпосмотрим расписание?\n', reply_markup=markup)

    elif message.from_user.id == '669076138' and get_name(message): # добавить сравнение времени спикера и текущего времени
        markup = types.InlineKeyboardMarkup(row_width=1)
        questions = types.InlineKeyboardButton('Вопросы слушателей', callback_data='questions')
        timeline = types.InlineKeyboardButton('График выступлений', callback_data='timeline')
        ask_question = types.InlineKeyboardButton('Задать вопрос', callback_data='ask_question')
        about_bot = types.InlineKeyboardButton('Что я могу', callback_data='about')
        markup.add(questions, timeline, ask_question, about_bot)

        bot.send_message(message.chat.id, '\nвыбери нужный пункт', reply_markup=markup)

    else:

        markup=types.InlineKeyboardMarkup(row_width=1)
        timeline=types.InlineKeyboardButton('График выступлений', callback_data='timeline')
        ask_question=types.InlineKeyboardButton('Задать вопрос', callback_data='ask_question')
        about_bot=types.InlineKeyboardButton('Что я могу', callback_data='about')
        markup.add(timeline, ask_question, about_bot)

        bot.send_message(message.chat.id, '\nвыбери нужный пункт', reply_markup=markup)
        get_name_visitor(message)


@bot.callback_query_handler(func=lambda call:True)
def callback(call):
    if call.data == 'about': # готово
        text = 'Я расскажу какие ожидаются выступления, а еще через меня можно задать вопрос спикеру!\n\n для возврата домой отправь мне сообщение\n'
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                text=f'\n{text}',
                                parse_mode='Markdown')

    elif call.data == 'timeline': # Готово
        markup = types.InlineKeyboardMarkup(row_width=1)
        home = types.InlineKeyboardButton('Домой', callback_data='home')
        markup.add(home)

        for number, meet in enumerate(get_timeline()):
            speaker = meet[0]
            start_time = meet[1]
            end_time = meet[2]
            meet_theme = meet[3]
            if number == 0:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                      text=f'\nс {start_time} до {end_time} тема: {meet_theme} спикер {speaker}')
                time.sleep(0.5)
            elif number == len(get_timeline())-1:
                bot.send_message(call.message.chat.id,
                                 text=f'\nс {start_time} до {end_time} тема: {meet_theme} спикер {speaker}',
                                 reply_markup=markup)
                time.sleep(0.5)
            else:
                bot.send_message(call.message.chat.id, text=f'\nс {start_time} до {end_time} тема: {meet_theme} спикер {speaker}')
                time.sleep(0.5)

    elif call.data == 'timeline2': # Готово
        markup = types.InlineKeyboardMarkup(row_width=2)
        start = types.InlineKeyboardButton('Начал', callback_data='start')
        finish = types.InlineKeyboardButton('Закончил', callback_data='finish')
        change = types.InlineKeyboardButton('Изменить', callback_data='change')
        markup.add(start, finish, change)

        for number, meet in enumerate(get_timeline()):
            in_process = 'не идет'
            if meet[4] == 'True':
                in_process = 'идет'
            speaker = meet[0]
            start_time = meet[1]
            end_time = meet[2]
            meet_theme = meet[3]
            if number == 0:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                      text=f'\nс {start_time} до {end_time} тема: {meet_theme}\n спикер {speaker}.\nВыступление {in_process}',
                                      reply_markup=markup)
                time.sleep(0.5)
            else:
                bot.send_message(call.message.chat.id, text=f'\nс {start_time} до {end_time} тема: {meet_theme}\n спикер {speaker}.\nВыступление {in_process}',
                                 reply_markup=markup)
                time.sleep(0.5)
        bot.send_message(call.message.chat.id, text='\n\n для возврата домой отправь мне сообщение\n')

    elif call.data == 'start':
        markup = types.InlineKeyboardMarkup(row_width=1)
        timeline = types.InlineKeyboardButton('Вернуться к графику', callback_data='timeline2')
        markup.add(timeline)
        now_time()

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='\nвыступление началось\n\n для возврата домой отправь мне сообщение\n', reply_markup=markup)

    elif call.data == 'ask_question': # готово
        markup = types.InlineKeyboardMarkup(row_width=2)

        ask = types.InlineKeyboardButton('Спросить', callback_data='ask')
        markup.add(ask)
        sent = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                     text='\nЗадай свой вопрос\n\n', reply_markup=markup)
        bot.register_next_step_handler(sent, get_question)

    elif call.data == 'ask': # готово
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                              text='\nСпасибо за вопрос\n\n для возврата домой отправь мне сообщение\n')

    elif call.data == 'questions': ### будет брать вопросы из БД для конкретного спикера? НЕ УДАЛЯЕТ ПРИ ОБНОВЛЕНИИ
        markup = types.InlineKeyboardMarkup(row_width=2)
        update = types.InlineKeyboardButton('Обновить', callback_data='questions')
        markup.add(update)
        for number, question in enumerate(get_my_questions()):
            visitor_name = question[0]
            visitor_question = question[2]
            if number == len(get_my_questions())-1:
                bot.send_message(call.message.chat.id, text=f'\n{visitor_name} справшивает:\n{visitor_question}\n\n для возврата домой отправь мне сообщение\n', reply_markup=markup)
                time.sleep(0.5)
            else:
                bot.send_message(call.message.chat.id, text=f'\n{visitor_name} справшивает:\n{visitor_question}\n\n')
                time.sleep(0.5)

    # elif call.data == 'home':
    #     bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
    #     start(call.message)


class Command(BaseCommand):
    help = 'телеграм бот собраний'

    def handle(self, *args, **options):
        print(bot.get_me())
        while True:
            try:
                bot.polling(none_stop=True)
            except Exception as error:
                print(error)
                time.sleep(5)
