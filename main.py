import telebot
from telebot.types import ReplyKeyboardMarkup
import time
from random import choice
from manual import game_manual, suits, number_card

secret_key = "6469799645:AAF3NE6vQ5dBpsCLB4FL-yNnId89Q3APtjU"
bot = telebot.TeleBot(secret_key)

storage = dict()


def init_storage(user_id):
    storage[user_id] = dict(rounds=None, counter_rounds=None, player_points=None)


def set_data_storage(user_id, key, value):
    storage[user_id][key] = value


def get_data_storage(user_id):
    return storage[user_id]


# Старт игры
@bot.message_handler(commands=['start'])
def commands(message):
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('Да', 'Нет')
    if message.text == '/start':
        user_name = message.from_user.first_name
        bot_msg = f"Добро пожаловать в игру, {user_name}!"
        bot.send_message(message.from_user.id, f'{bot_msg}')
        time.sleep(1)
        bot.send_message(message.from_user.id, f'Вы готовы поиграть со мной?', reply_markup=markup)
        bot.register_next_step_handler(message, agreement_to_play)


@bot.message_handler(content_types=['text'])
# Согласие играть: да или нет
def agreement_to_play(message):
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('Да', 'Нет')
    msg = message.text.lower().strip()
    if msg not in ['да', 'нет']:
        msg = bot.reply_to(message, f'Упс!\nЯ не понимаю, что Вы хотите мне сказать 😔 \n'
                                    f'Давайте лучше сыграем?', reply_markup=markup)
        bot.register_next_step_handler(msg, agreement_to_play)

    if msg == 'да':
        msg = bot.reply_to(message, 'Хотели бы Вы прочитать правила игры?', reply_markup=markup)
        bot.register_next_step_handler(msg, manual)
    elif msg == 'нет':
        bot.send_message(message.from_user.id, 'Очень жаль, что Вы не захотели играть!\n'
                                               'Для начала игры введите "/start"')


# Вывод правил по просьбе пользователя
def manual(message):
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    msg = message.text.lower().strip()
    if msg not in ['да', 'нет']:
        msg = bot.reply_to(message, f'Я не понимаю, что Вы хотите мне сказать 😔 \n'
                                    f'Хотите ознакомиться с правилами?', reply_markup=markup)
        bot.register_next_step_handler(msg, manual)
        return
    markup.add('Лёгкий', 'Сложный')
    if msg == 'да':
        bot.send_message(message.from_user.id, f'{game_manual}\n{suits}\n{number_card}\n')
        time.sleep(1)
        bot.send_message(message.from_user.id, f'\nА теперь давайте приступим к игре!')
        time.sleep(1)
        bot.send_message(message.from_user.id, f'Выберите уровень сложности игры', reply_markup=markup)
        bot.register_next_step_handler(message, game_difficulty)
    elif msg == 'нет':
        bot.send_message(message.from_user.id, f'Выберите уровень сложности игры', reply_markup=markup)
        bot.register_next_step_handler(message, game_difficulty)


# Получение случайной карты
def random_card():
    card_number = ["6", "7", "8", "9", "10", "Валет", "Дама", "Король", "Туз"]  # Выбор карты
    card_suit = ["Черви", "Буби", "Трефы", "Пики"]  # Выбор масти
    random_card_number = choice(card_number)  # Случайная карта
    random_card_suit = choice(card_suit)  # Случайная масть
    random_card = random_card_number + ' | ' + random_card_suit  # Случайная загаданная карта
    return [random_card_number, random_card_suit, random_card]


# Выбор уровня сложности
def game_difficulty(message):
    user_answer = message.text.lower().replace('ё', 'е').strip()
    init_storage(message.from_user.id)
    rounds = 3
    counter_rounds = 1  # Подсчёт сыгранных раундов
    player_points = 0  # Подсчёт набранных очков за попеду
    set_data_storage(message.from_user.id, 'rounds', rounds)
    set_data_storage(message.from_user.id, 'counter_rounds', counter_rounds)
    set_data_storage(message.from_user.id, 'player_points', player_points)
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    if user_answer not in ['легкий', 'сложный']:
        msg = bot.reply_to(message, f'Я не понимаю, что Вы хотите мне сказать 😔 \n'
                                    f'Выберите уровень сложности!', reply_markup=markup)
        bot.register_next_step_handler(msg, game_difficulty)
        return
    if user_answer == 'легкий':
        bot.send_message(message.from_user.id, 'Вы выбрали лёгкий уровень сложности')
        time.sleep(1)
        bot.send_message(message.from_user.id, f'Вы играете раунд: {counter_rounds}')
        markup.add('🟥', '⬛️')
        time.sleep(1)
        bot.send_message(message.from_user.id, 'Попробуйте отгадать цвет карты, которую я загадал',
                         reply_markup=markup)
        bot.register_next_step_handler(message, easy_game)
    elif user_answer == 'сложный':
        bot.send_message(message.from_user.id, 'Вы выбрали тяжёлый уровень сложности')
        time.sleep(1)
        bot.send_message(message.from_user.id, f'Вы играете раунд: {counter_rounds}')
        markup.add("6", "7", "8", "9", "10", "Валет", "Дама", "Король", "Туз")
        bot.send_message(message.from_user.id, 'Как Вы думаете, какая у меня карта?', reply_markup=markup)
        bot.register_next_step_handler(message, hard_game)


def easy_game(message):  # Если игрок выбрал лёгкую сложность
    correct_card = random_card()
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('🟥', '⬛️')

    rounds = get_data_storage(message.from_user.id)['rounds']
    counter_rounds = get_data_storage(message.from_user.id)['counter_rounds']
    player_points = get_data_storage(message.from_user.id)['player_points']

    if message.text.lower().replace('ё', 'е').strip() not in ['🟥', '⬛️', 'красный', 'черный']:
        msg = bot.reply_to(message, 'Пожалуйста, выберете корректный ответ!', reply_markup=markup)
        bot.register_next_step_handler(msg, easy_game)
        return

    msg = message.text.lower().replace('ё', 'е').strip()
    if (msg == '🟥' or msg == 'красный') and correct_card[1] in ['Черви', 'Буби']:
        counter_rounds += 1
        set_data_storage(message.from_user.id, 'counter_rounds', counter_rounds)
        player_points += 1
        set_data_storage(message.from_user.id, 'player_points', player_points)
        bot.send_message(message.from_user.id, f'Молодец!\nВы правильно угадали мою карту!'
                                               f'\nЯ загадал: {correct_card[2]}')
    elif (msg == '⬛️' or msg == 'черный') and correct_card[1] in ['Пики', 'Трефы']:
        counter_rounds += 1
        set_data_storage(message.from_user.id, 'counter_rounds', counter_rounds)
        player_points += 1
        set_data_storage(message.from_user.id, 'player_points', player_points)
        bot.send_message(message.from_user.id, f'Молодец!\n'
                                               f'Вы правильно угадали мою карту!\nЯ загадал: {correct_card[2]}')
    else:
        counter_rounds += 1
        set_data_storage(message.from_user.id, 'counter_rounds', counter_rounds)
        bot.send_message(message.from_user.id, f'Упс!\nВы не угадали.\nМоя карта: {correct_card[2]}')
    if counter_rounds <= rounds:
        bot.send_message(message.from_user.id, f'Вы играете раунд: {counter_rounds}', reply_markup=markup)
        bot.register_next_step_handler(message, easy_game)
    elif counter_rounds > rounds:
        end_game(message)


def hard_game(message):  # Если игрок выбрал трудную сложность
    rounds = get_data_storage(message.from_user.id)['rounds']
    counter_rounds = get_data_storage(message.from_user.id)['counter_rounds']
    player_points = get_data_storage(message.from_user.id)['player_points']
    correct_card = random_card()
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("6", "7", "8", "9", "10", "Валет", "Дама", "Король", "Туз")

    if message.text.lower().strip() not in ["6", "7", "8", "9", "10", "валет", "дама", "король", "туз"]:
        msg = bot.reply_to(message, 'Пожалуйста, выберете корректный ответ!', reply_markup=markup)
        bot.register_next_step_handler(msg, hard_game)
        return
    msg = message.text.lower().strip()
    if msg == correct_card[0].lower():
        counter_rounds += 1
        set_data_storage(message.from_user.id, 'counter_rounds', counter_rounds)
        player_points += 1
        set_data_storage(message.from_user.id, 'player_points', player_points)
        bot.send_message(message.from_user.id, f'Молодец!\nВы правильно угадали мою карту!\n'
                                               f'Я загадал: {correct_card[2]}')
    else:
        counter_rounds += 1
        set_data_storage(message.from_user.id, 'counter_rounds', counter_rounds)
        bot.send_message(message.from_user.id, f'Очень жаль! Вам не удалось отгадать.'
                                               f'\nМоя карта: {correct_card[2]}')
    if counter_rounds <= rounds:
        bot.send_message(message.from_user.id, f'Вы играете раунд: {counter_rounds}', reply_markup=markup)
        bot.register_next_step_handler(message, hard_game)
    elif counter_rounds > rounds:
        end_game(message)


# Вывод результатов по игре
def end_game(message):
    player_points = get_data_storage(message.from_user.id)['player_points']
    if player_points < 2:
        bot.send_message(message.from_user.id, f'Очень жаль!\nВы проиграли!')
    elif player_points == 2:
        bot.send_message(message.from_user.id, f'Мои поздравления!\nВы выиграли!')
    elif player_points == 3:
        bot.send_message(message.from_user.id, f'Вам нет равных!\nВы набрали максимальное количество баллов!')
    time.sleep(1)
    bot.send_message(message.from_user.id, f'Количество Ваших баллов: {player_points}')
    time.sleep(1)
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('Да', 'Нет')
    bot.send_message(message.from_user.id, 'Хотели бы Вы сыграть еще раз?', reply_markup=markup)
    bot.register_next_step_handler(message, agreement_to_play)


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=2)
