from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from crud_functions2 import *

api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())


kb_1 = InlineKeyboardMarkup(resize_keyboard=True)
button1 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button2 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
kb_1.row(button1, button2)

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button_1 = KeyboardButton(text='Рассчитать')
button_2 = KeyboardButton(text='Информация')
button_3 = KeyboardButton(text='Купить')
button_4 = KeyboardButton(text='Регистрация')
kb.row(button_1, button_2, button_3, button_4)

kb_buy = InlineKeyboardMarkup(resize_keyboard=True)
button_buy1 = InlineKeyboardButton(text='Product1', callback_data="product_buying")
button_buy2 = InlineKeyboardButton(text='Product2', callback_data="product_buying")
button_buy3 = InlineKeyboardButton(text='Product3', callback_data="product_buying")
button_buy4 = InlineKeyboardButton(text='Product4', callback_data="product_buying")
kb_buy.row(button_buy1, button_buy2)
kb_buy.row(button_buy3, button_buy4)



class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

@dp.message_handler(commands = ['start'])
async def start_(message):
    await message.answer(text='Привет! Я бот, помогающий твоему здоровью.', reply_markup=kb)



@dp.message_handler(text = 'Рассчитать')
async def main_menu(message):
    await message.answer(text='Выберите опцию:', reply_markup=kb_1)

@dp.message_handler(text = ['Информация'])
async def inform(message):
    await message.answer('Этот бот поможет рассчитать ежедневные калории.')

@dp.message_handler(text='Купить')
async def get_buying_list(message):
    products = get_all_products()
    for i in range(1, 5):
        await message.answer(f"Продукт: Product{i} | Описание: описание {i} | Цена: {i * 100}")
        await bot.send_photo(message.from_user.id, photo=open(f'p{i}.jpg', 'rb'))

    await  message.answer('Выберите продукт для покупки: ', reply_markup=kb_buy)

@dp.callback_query_handler(text= ['product_buying'])
async def send_confirm_message(call):
    await  call.message.answer('Вы успешно приобрели продукт!')
    await call.answer()

@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('(10 x вес(кг)) +(6,25 x рост(см)) – (5 x возраст(г) + 5')

@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()




@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост:')
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    data = await state.get_data()
    await message.answer('Введите свой вес:')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    result = (10 * int(data['weight']) + 6.25 * int(data['growth']) - 5 * int(data['age']) + 5)
    await message.answer(f"Ваша норма калорий: {result} ккал в сутки.")
    await state.finish()


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = 1000


@dp.message_handler(text="Регистрация")
async def sing_up(message):
    await message.answer("Введите имя пользователя (только латинский алфавит):")
    await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    await state.update_data(username=message.text)
    data = await state.get_data()
    user = is_included(data['username'])
    if user is True:
        await state.update_data(username=message.text)
        await message.answer("Введите свой email:")
        await RegistrationState.email.set()
    else:
        await message.answer("Пользователь существует, введите другое имя")
        await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    await state.update_data(email=message.text)
    await message.answer("Введите свой возраст:")
    await RegistrationState.age.set()


@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    await state.update_data(age=message.text)
    data = await state.get_data()
    add_user(data['username'], data['email'], data['age'])
    await message.answer('Регистрация прошла успешно.')
    await state.finish()







@dp.message_handler()
async def start_any(message):
    await message.answer('Введите команду /start чтобы начать общение')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)








