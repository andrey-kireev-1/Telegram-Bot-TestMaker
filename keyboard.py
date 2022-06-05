from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


button_start_test = KeyboardButton("/Пройти_тест")
button_create_test = KeyboardButton("/Создать_тест")

start_keyboard = ReplyKeyboardMarkup(resize_keyboard = True) #Клавиатура на старте
start_keyboard.add(button_start_test, button_create_test)

button_add_question = KeyboardButton("/Добавить_вопрос")
button_exit_creation = KeyboardButton("/Завершить_создание")

add_question_keyboard = ReplyKeyboardMarkup(resize_keyboard = True) #Клавиатура добавления вопроса
add_question_keyboard.add(button_add_question, button_exit_creation)

button_exit = KeyboardButton("/Выйти")

run_question_keyboard = ReplyKeyboardMarkup(resize_keyboard = True) #Клавиатура добавления вопроса
run_question_keyboard.add(button_exit)


def answer_variants(id, variants): #Инлайновая клавиатура выбора варианта ответа
    i = 0
    ideologies_inline_keyboard = InlineKeyboardMarkup()
    while (i < len(variants)):
        tmp = f"{variants[i]}"
        button_ideology = InlineKeyboardButton(tmp, callback_data=f"udeo_{id}_{i}")
        ideologies_inline_keyboard.add(button_ideology)
        i += 1
    return ideologies_inline_keyboard