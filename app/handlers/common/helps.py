from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.chat_action import ChatActionSender

from app.core.bot import bot
from app.forms.subscription import SupportForm
from app.keyboards.inline import (
    device_inline_kb,
    keys_inline_kb,
    protocol_inline_kb)
from app.messages.common import CommonMessage

router = Router()


@router.callback_query(F.data == 'get_ref_url')
async def get_ref_url(call: CallbackQuery, current_user: dict):
    """CallBack запрос для получения реферальной ссылки."""
    await call.answer('Загружаю информацию по реферам', show_alert=False)
    # TODO: Выдавать информацию пользователю о его текущем состоянии бонусов
    async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
        await call.message.delete()
        await call.message.answer(CommonMessage.REFERRAL_MESSAGE.format(
            user_id=call.from_user.id),
                                  reply_markup=keys_inline_kb(True))


@router.callback_query(F.data == 'get_price')
async def get_price(call: CallbackQuery):
    """CallBack запрос для получения информации по стоимости."""
    await call.answer('Загружаю информацию по ценам', show_alert=False)
    async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
        await call.message.delete()
        await call.message.answer(CommonMessage.PRICE_MESSAGE,
                                  reply_markup=keys_inline_kb(False))


@router.callback_query(F.data == 'get_help')
async def get_help(call: CallbackQuery, state: FSMContext):
    """CallBack запрос для получения инструкций."""
    await call.answer('Загружаю информацию с инструкциями', show_alert=False)
    async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
        await call.message.delete()
        await call.message.answer('Выберите протокол подключения:',
                                  reply_markup=protocol_inline_kb())
    await state.set_state(SupportForm.protocol)


@router.callback_query(SupportForm.protocol)
async def choice_device(call: CallbackQuery, state: FSMContext):
    """CallBack запрос для выбора устройства."""
    await state.update_data(protocol=call.data)
    data = await state.get_data()
    protocol = data.get('protocol')
    await call.answer('Загружаю информацию с инструкциями', show_alert=False)
    await call.message.delete()
    await call.message.answer('Выберите устройство:',
                              reply_markup=device_inline_kb(protocol))


# TODO: Пересылать сообщения администраторам или в бот где подключен ИИ
@router.callback_query(F.data == 'get_support')
async def get_support(call: CallbackQuery, state: FSMContext,
                      current_user: dict):
    """CallBack запрос для обращения в поддержку."""
    await call.answer('Перевожу на техническую поддержку', show_alert=False)
    await call.message.delete()
    await call.message.answer('Расскажи о своей проблеме, '
                              f'{call.from_user.first_name}')
