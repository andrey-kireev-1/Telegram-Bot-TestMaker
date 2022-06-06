from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import hashlib
import sqlite3
from config import DB_FILENAME, TOKEN
from storage import storage
import keyboard

bot = Bot(token=TOKEN)
storage_for_form = MemoryStorage()
dp = Dispatcher(bot, storage=storage_for_form)


class FSMForm(StatesGroup):
    question = State()
    answer = State()

class FSMForm2(StatesGroup):
    results =State()
    name = State()
    description = State()

class FSMForm3(StatesGroup):
    key = State()


def get_result(user):
    count_res = len(storage[user]["results"])
    border_percent = 100 / count_res
    new_max = storage[user]["max"] - storage[user]["min"]
    new_min = 0
    new_pressed = storage[user]["pressed"] - storage[user]["min"]
    new_pressed_percent = (new_pressed / new_max) * 100
    i = 0
    while new_pressed_percent > border_percent:
        new_pressed_percent -= border_percent
        i += 1
    return storage[user]["results"][i]


#Стартовая позиция бота
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    print(f"User {message.from_user.username} starts bot")
    str1 = "Вы можете пройти тест или создать свой"
    await bot.send_message(message.from_user.id, str1, reply_markup=keyboard.start_keyboard)
    str1 = "Что вы хотите сделать?"
    await bot.send_message(message.from_user.id, str1, reply_markup=keyboard.start_keyboard)

#Команда для создания теста
@dp.message_handler(commands=["Создать_тест"])
async def create_test(message: types.Message):
    storage[f"user{message.from_user.id}"] = {"test_name" : "", "test_description" : "", "question_text" : "", "question_answers": "", "question_answers_rate": "", "results": ""} #Создание хранилище для конкретного пользователя
    str1 = "Введите вопрос:"
    await FSMForm.question.set()
    await bot.send_message(message.from_user.id, str1, reply_markup=keyboard.ReplyKeyboardRemove())

#Команда для добавления вопроса
@dp.message_handler(commands=["Добавить_вопрос"])
async def create_test(message: types.Message):
    str1 = "Введите вопрос:"
    await FSMForm.question.set()
    await message.reply(str1, reply_markup=keyboard.ReplyKeyboardRemove())
    
@dp.message_handler(commands=["Пройти_тест"])
async def run_test(message: types.Message):
    storage[f"user{message.from_user.id}"] = {}
    str1 = "Отправьте ключ к тесту:"
    await FSMForm3.key.set()
    await message.reply(str1, reply_markup=keyboard.ReplyKeyboardRemove())

@dp.message_handler(state=FSMForm3.key)
async def read_key(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['key'] = message.text
    storage[f"user{message.from_user.id}"] = {"question_text" : "", "question_answers": "", "question_answers_rate": "", "results": "", "question_index": 0}
    conn = sqlite3.connect(DB_FILENAME)
    cur = conn.cursor()
    cur.execute('SELECT * FROM users_tests WHERE hash = ?', (data["key"],))
    print("execution")
    conn.commit()
    rows = cur.fetchall()
    owner = ""
    name = ""
    descr = ""
    for row in rows:
        owner = row[1]
        name = row[2]
        descr = row[3]
        storage[f"user{message.from_user.id}"]["question_text"] = row[4]
        storage[f"user{message.from_user.id}"]["question_answers"] = row[5]
        storage[f"user{message.from_user.id}"]["question_answers_rate"] = row[6]
        storage[f"user{message.from_user.id}"]["results"] = row[7]
    str1 = f"Название теста: {name}\nСоздатель теста: {owner}\nОписание: {descr}"
    await bot.send_message(message.from_user.id, str1, reply_markup=keyboard.ReplyKeyboardRemove())
    await state.finish()
    arr_q = storage[f"user{message.from_user.id}"]["question_text"].removeprefix("||")
    arr_q = arr_q.split("||")
    print(arr_q)
    storage[f"user{message.from_user.id}"]["question_text"] = arr_q
    arr_q_a = storage[f"user{message.from_user.id}"]["question_answers"].removeprefix("||")
    arr_q_a = arr_q_a.split("||")
    i = 0
    for item in arr_q_a:
        item = item.removeprefix(";")
        arr_q_a[i] = item.split(";")
        i += 1
    print(arr_q_a)
    storage[f"user{message.from_user.id}"]["question_answers"] = arr_q_a
    arr_q_a_r = storage[f"user{message.from_user.id}"]["question_answers_rate"].removeprefix("||")
    arr_q_a_r = arr_q_a_r.split("||")
    i = 0
    for item in arr_q_a_r:
        item = item.removeprefix(";")
        arr_q_a_r[i] = item.split(";")
        i += 1
    print(arr_q_a_r)
    storage[f"user{message.from_user.id}"]["question_answers_rate"] = arr_q_a_r
    arr_res = (storage[f"user{message.from_user.id}"]["results"]).split("\n")
    storage[f"user{message.from_user.id}"]["results"] = arr_res
    storage[f"user{message.from_user.id}"]["pressed"] = 0
    storage[f"user{message.from_user.id}"]["max"] = 0
    storage[f"user{message.from_user.id}"]["min"] = 0
    inline_keyboard = keyboard.answer_variants(message.from_user.id, storage[f"user{message.from_user.id}"]["question_answers"][storage[f"user{message.from_user.id}"]["question_index"]])
    await bot.send_message(message.from_user.id, storage[f"user{message.from_user.id}"]["question_text"][storage[f"user{message.from_user.id}"]["question_index"]], reply_markup=inline_keyboard)


def processing(user, pressed_index):
    max = -99999
    min = 99999
    for number in storage[user]["question_answers_rate"][storage[user]["question_index"]]:
        if int(number) > max:
            max = int(number)
        if int(number) < min:
            min = int(number)
        if int(number) == int(storage[user]["question_answers_rate"][storage[user]["question_index"]][pressed_index]):
            storage[user]["pressed"] += int(number)
    storage[user]["max"] += max
    storage[user]["min"] += min



@dp.callback_query_handler(text_contains = 'udeo_')
async def process_callback_btn(callback_query: types.CallbackQuery):
    c_data = callback_query.data.split("_") #Колбэк дата = "udeo_Индекс идеологии_IDПользователя"
    print(c_data)
    pressed_index = c_data[2]
    user = f"user{c_data[1]}"
    print(f"callback {user}")
    processing(user, int(pressed_index))
    if storage[f"user{c_data[1]}"]["question_index"] < len(storage[f"user{c_data[1]}"]["question_text"])-1:
        storage[f"user{c_data[1]}"]["question_index"] += 1
        inline_keyboard = keyboard.answer_variants(c_data[1], storage[f"user{c_data[1]}"]["question_answers"][storage[f"user{c_data[1]}"]["question_index"]])
        await bot.send_message(c_data[1], storage[f"user{c_data[1]}"]["question_text"][storage[f"user{c_data[1]}"]["question_index"]], reply_markup=inline_keyboard)
    else:
        str_res = get_result(f"user{c_data[1]}")
        await bot.send_message(c_data[1], "Ваш результат:", reply_markup=keyboard.ReplyKeyboardRemove())
        await bot.send_message(c_data[1], str_res, reply_markup=keyboard.start_keyboard)







#Команда для завершения создания теста
@dp.message_handler(commands=["Завершить_создание"])
async def exit_test(message: types.Message):
    str1 = "Введите результаты:"
    await FSMForm2.results.set()
    await message.reply(str1, reply_markup=keyboard.ReplyKeyboardRemove())

@dp.message_handler(state=FSMForm2.results)
async def add_results(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['results'] = message.text
    storage[f"user{message.from_user.id}"]["results"] = data['results']
    str1 = "Введите название теста:"
    await FSMForm2.next()
    await message.reply(str1)

@dp.message_handler(state=FSMForm2.name)
async def add_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    storage[f"user{message.from_user.id}"]["test_name"] = data['name']
    str1 = "Введите описание теста:"
    await FSMForm2.next()
    await message.reply(str1)

@dp.message_handler(state=FSMForm2.description)
async def add_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
    storage[f"user{message.from_user.id}"]["test_description"] = data['description']
    user_test_key = ""
    user_test_key = f"user{message.from_user.id}" + storage[f"user{message.from_user.id}"]["test_name"]
    print(user_test_key)
    user_test_key = hashlib.sha256(user_test_key.encode('utf-8')).hexdigest()
    print(user_test_key)

    await state.finish()
    str1 = f"Ваш персональный ключ для доступа к тесту: {user_test_key}"

    try:
        conn = sqlite3.connect(DB_FILENAME)
        cur = conn.cursor()
        cur.execute(f'INSERT INTO users_tests VALUES("{user_test_key}", "@{message.from_user.username}","{storage[f"user{message.from_user.id}"]["test_name"]}", "{storage[f"user{message.from_user.id}"]["test_description"]}", "{storage[f"user{message.from_user.id}"]["question_text"]}", "{storage[f"user{message.from_user.id}"]["question_answers"]}", "{storage[f"user{message.from_user.id}"]["question_answers_rate"]}", "{storage[f"user{message.from_user.id}"]["results"]}")')
        print("execution")
        conn.commit()
        storage[f"user{message.from_user.id}"] = {}
    except:
        print("Ошибка записи")

    await bot.send_message(message.from_user.id, str1, reply_markup=keyboard.start_keyboard)
    




@dp.message_handler(state=FSMForm.question)
async def add_question(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['question'] = message.text
    storage[f"user{message.from_user.id}"]["question_text"] = storage[f"user{message.from_user.id}"]["question_text"] + "||" + data['question']
    str1 = "Введите варианты"
    await FSMForm.next()
    await message.reply(str1)

@dp.message_handler(state=FSMForm.answer)
async def add_answer(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['answer'] = message.text
    answers = data['answer'].split("\n")
    i = 0 
    for item in answers:
        answers[i] = item.split(";")
        i += 1
    print(answers)
    a = ""
    a_r = ""
    try:
        for item in answers:
            if item[1][0] == "+" or item[1][0] == "-" or item[1][0] == "0":
                a = a + ";" + item[0]
                a_r = a_r + ";" + item[1]
            else:
                print("ОШИБКА")
                a = "Err"
                storage[f"user{message.from_user.id}"]["question_text"] = storage[f"user{message.from_user.id}"]["question_text"].removesuffix(f"||{data['question']}")
                await message.reply("Варианты ответов введены не верно!\nВопрос не записан!")
                break
        if a != "Err":
            storage[f"user{message.from_user.id}"]["question_answers"] = storage[f"user{message.from_user.id}"]["question_answers"] + "||" + a
            storage[f"user{message.from_user.id}"]["question_answers_rate"] = storage[f"user{message.from_user.id}"]["question_answers_rate"] + "||" + a_r
    except:
        print("ОШИБКА")
        storage[f"user{message.from_user.id}"]["question_text"] = storage[f"user{message.from_user.id}"]["question_text"].removesuffix(f"||{data['question']}")
        await message.reply("Варианты ответов введены не верно!\nВопрос не записан!")
    str1 = "Добавить еще вопрос?"
    await state.finish()
    await bot.send_message(message.from_user.id, str1, reply_markup=keyboard.add_question_keyboard)




#Команда для создания теста
@dp.message_handler(commands=["Мои_тесты"])
async def get_my_tests(message: types.Message):
    conn = sqlite3.connect(DB_FILENAME)
    cur = conn.cursor()
    cur.execute('SELECT * FROM users_tests WHERE owner = ?', (f"@{message.from_user.username}",))
    print("execution")
    conn.commit()
    rows = cur.fetchall()
    for row in rows:
        print(row)




@dp.message_handler() #Отлов сообщений не соответствующих командам
async def check_another_messages(message: types.Message):
    try:
        conn = sqlite3.connect(DB_FILENAME)
        cur = conn.cursor()
        cur.execute(f'INSERT INTO users VALUES("{message.from_user.id}", "@{message.from_user.username}","{message.text}")')
        print("execution")
        conn.commit()
        sql_query = """SELECT * from users"""
        cur.execute(sql_query)
        rows = cur.fetchall()
        print (len(rows))
    except Exception as e:
        print(e)
        conn = sqlite3.connect(DB_FILENAME)
        cur = conn.cursor()
        cur.execute(f'INSERT INTO users VALUES("{message.from_user.id}")')
        conn.commit()
        





if __name__ == '__main__':
    executor.start_polling(dp)