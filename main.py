from flask import Flask, request, Response
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.messages import KeyboardMessage
from Settings import TOKEN
import json
import random
import datetime
from database import MyDataBase

with open('english_words.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

app = Flask(__name__)

bot_configuration = BotConfiguration(
    name='OrcaVV',
    avatar='http://viber.com/avatar.jpg',
    auth_token=TOKEN
)

viber = Api(bot_configuration)


class Game:
    def __init__(self, viber_id):
        self.viber_id = viber_id
        self.word = {}
        self.count_all = 0
        self.count_correct = 0


START_KBD = {
    "Type": "keyboard",
    "Buttons": [
        {
            "Columns": 6,
            "Rows": 1,
            "BgColor": "#e6f5ff",
            "BgMedia": "http://link.to.button.image",
            "BgMediaType": "picture",
            "BgLoop": True,
            "ActionType": "reply",
            "ActionBody": "Старт",
            "ReplyType": "message",
            "Text": "Старт"
        }
    ]
}

message = KeyboardMessage(tracking_data='tracking_data', keyboard=START_KBD)


def next_word(game):
    db = MyDataBase('database.db')
    user_id = db.find_user(game.viber_id)[0][0]
    game.word = data[random.choice(range(50))]
    learning = db.find_learning(user_id, game.word['word'])
    if len(learning) == 0:
        db.add_learning(user_id, game.word['word'], datetime.datetime.now())
    else:
        correct_answer = learning[0]['correct_answer']
        if correct_answer >= 3:
            next_word(game)
    db.close()


# вопрос
def question(game):
    count_all = game.count_all

    if count_all <= 3:
        # вывести вопрос
        next_word(game)
        bot_response = TextMessage(text=f'{count_all + 1}. Перевод слова: {game.word["word"]}',
                                   keyboard=CreateKBD(game), tracking_data='tracking_data')
        viber.send_messages(game.viber_id, [bot_response])
    else:
        # вывести итоги раунда
        count_correct = game.count_correct
        bot_response = TextMessage(text=f"Верно {count_correct} из {count_all}", keyboard=START_KBD,
                                   tracking_data='tracking_data')
        viber.send_messages(game.viber_id, [bot_response])


# обработать ответ
def answer(text, game):
    db = MyDataBase('database.db')
    user_id = db.find_user(game.viber_id)[0]
    if text == game.word["translation"]:
        # счётчик правильных ответов
        game.count_correct += 1
        db.update_learning(user_id, game.word['word'])
        bot_response = TextMessage(text='Правильно')
    else:
        bot_response = TextMessage(text='Неправильно')
    # всего ответов
    game.count_all += 1
    viber.send_messages(game.viber_id, [bot_response])
    question(game)


# привести пример
def example(game, number):
    bot_response = TextMessage(text=f'{game.word["examples"][number]}',
                               keyboard=CreateKBD(game), tracking_data='tracking_data')
    keyboard = KeyboardMessage(tracking_data='tracking_data', keyboard=CreateKBD(game))
    viber.send_messages(game.viber_id, [bot_response])


# клавиатура ползователя
def CreateKBD(game):
    # список с вариантами переводов слова
    translation = []
    # правильный перевод
    translation.append(game.word["translation"])
    while len(translation) != 4:
        # заносим новое слово если его нет в списке
        if random.choice(data)["translation"] not in translation:
            translation.append(random.choice(data)["translation"])
        random.shuffle(translation)
    KEYBOARD = {
        "Type": "keyboard",
        "Buttons": [
            {
                "Columns": 3,
                "Rows": 1,
                "BgColor": "#e6f5ff",
                "BgMedia": "http://link.to.button.image",
                "BgMediaType": "picture",
                "BgLoop": True,
                "ActionType": "reply",
                "ActionBody": f"{translation[0]}",
                "ReplyType": "message",
                "Text": f"{translation[0]}"
            },
            {
                "Columns": 3,
                "Rows": 1,
                "BgColor": "#e6f5ff",
                "BgMedia": "http://link.to.button.image",
                "BgMediaType": "picture",
                "BgLoop": True,
                "ActionType": "reply",
                "ActionBody": f"{translation[1]}",
                "ReplyType": "message",
                "Text": f"{translation[1]}"
            },
            {
                "Columns": 3,
                "Rows": 1,
                "BgColor": "#e6f5ff",
                "BgMedia": "http://link.to.button.image",
                "BgMediaType": "picture",
                "BgLoop": True,
                "ActionType": "reply",
                "ActionBody": f"{translation[2]}",
                "ReplyType": "message",
                "Text": f"{translation[2]}"
            },
            {
                "Columns": 3,
                "Rows": 1,
                "BgColor": "#e6f5ff",
                "BgMedia": "http://link.to.button.image",
                "BgMediaType": "picture",
                "BgLoop": True,
                "ActionType": "reply",
                "ActionBody": f"{translation[3]}",
                "ReplyType": "message",
                "Text": f"{translation[3]}"
            },
            {
                "Columns": 6,
                "Rows": 1,
                "BgColor": "#e6f5ff",
                "BgMedia": "http://link.to.button.image",
                "BgMediaType": "picture",
                "BgLoop": True,
                "ActionType": "reply",
                "ActionBody": "Пример использования",
                "ReplyType": "message",
                "Text": "Пример использования"
            }
        ]
    }
    return KEYBOARD


# справочник соответствия пользователя и его текущей игры
user = {}


def poisk(viber_id):
    return user[viber_id]


# количество примеров перевода
count_example = 0


@app.route('/incoming', methods=['POST'])
def incoming():
    # обработка
    db = MyDataBase('database.db')
    viber_request = viber.parse_request(request.get_data())

    if isinstance(viber_request, ViberConversationStartedRequest):
        viber_user = viber_request.user.id
        if len(db.find_user(viber_user)) == 0:
            db.add_users(viber_request.user.name, viber_user, datetime.datetime.now())
            new_game = Game(viber_user)
            user[viber_user] = new_game
        text = 'Hello! Lets learn English \n' \
               f'Tap Start. Вы выучили {db.count_corrcect_word(viber_user)[0]} слов \n' \
               f'Время последнего посещения {db.last_visit(viber_user)[0][0:16]}'
        viber.send_messages(viber_user, [TextMessage(text=text, keyboard=START_KBD,
                                                     tracking_data='tracking_data')])
    if isinstance(viber_request, ViberMessageRequest):
        game = poisk(viber_request.sender.id)
        if isinstance(viber_request.message, TextMessage):
            if viber_request.message.text == "Старт":
                game.count_all = 0
                game.count_correct = 0
                question(game)
            # вызов примера использования
            elif viber_request.message.text == "Пример использования":
                global count_example
                example(game, count_example)
                # проверяем количетво примеров
                if count_example > len(game.word["examples"]):
                    count_example = 0
                else:
                    count_example += 1
            else:
                # ответ пользователя
                answer(viber_request.message.text, game)

    db.close()
    return Response(status=200)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=80)
