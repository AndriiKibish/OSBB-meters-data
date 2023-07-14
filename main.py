# coding: utf-8

import asyncio
import pandas as pd
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

# Определение состояний диалога
class Form(StatesGroup):
    COLUMN_NAMES = State()
    COLUMN_DATA = State()

# Создание бота и диспетчера
bot = Bot(token='6267123536:AAFzYfaaRvyNDB_mjkmgxELopJEj0It5Cu4')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Обработчик команды /start
@dp.message_handler(Command('start'))
async def start(message: types.Message):
    await message.answer('Введіть назви стовпців (через кому):')
    await Form.COLUMN_NAMES.set()

# Обработчик ввода названий столбцов
@dp.message_handler(state=Form.COLUMN_NAMES)
async def column_names(message: types.Message, state: FSMContext):
    column_names = message.text.split(',')
    await state.update_data(column_names=column_names)
    await state.update_data(column_data=[])
    await message.answer('Введіть дані для кожного стовпця через кому (надіслати /stop для завершення введення).')
    await Form.COLUMN_DATA.set()

# Обработчик ввода данных для каждого столбца
@dp.message_handler(state=Form.COLUMN_DATA)
async def column_data(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == '/stop':
            df = pd.DataFrame(data['column_data'], columns=data['column_names'])
            file_name = f"дані лічильників {datetime.now().strftime('%Y-%m-%d')}.xlsx"
            df.to_excel(file_name, index=False)

            with open(file_name, 'rb') as file:
                await message.answer_document(file)

            await message.answer('Таблиця збережена. До побачення!')
            await state.finish()
        else:
            column_data = message.text.split(',')
            data['column_data'].append(column_data)

# Главная функция
async def main():
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())