from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.chat_action import ChatActionSender

from app.core.bot import bot
from app.core.config import settings
from app.forms.subscription import SubscriptionForm
from app.keyboards.inline import (
    choice_duration_kb,
    choice_location_kb,
    choice_protocol_kb,
    choice_sub_inline_kb,
    choice_type_inline_kb,
    keys_inline_kb,
    subscription_inline_kb)
from app.messages.common import CommonMessage
from app.schemas.subscription import SubscriptionCreate, SubscriptionType

router = Router()


@router.callback_query(F.data == 'pay_subscription')
async def pay_subscription(call: CallbackQuery, state: FSMContext,
                           current_user: dict):
    """CallBack запрос для покупки или продления подписки."""
    await state.clear()
    await call.answer(CommonMessage.LOAD_MSG_CHOICE_SUB, show_alert=False)
    if current_user.get('subscription'):
        async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
            await call.message.delete()
            await call.message.answer(
                CommonMessage.CHOICE_MSG_NEW_OR_OLD,
                reply_markup=choice_sub_inline_kb())
    else:
        async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
            url = settings.get_backend_url + settings.SERVER_PATH
            async with call.bot.http_client.get(url) as response:
                servers = await response.json()
            await state.update_data(servers=servers)
            await call.message.delete()
            await call.message.answer(
                CommonMessage.CHOICE_MSG_TYPE_SUB,
                reply_markup=choice_type_inline_kb(trial=True))
            await state.set_state(SubscriptionForm.type)


@router.callback_query(F.data == 'get_trial')
async def get_trial(call: CallbackQuery, state: FSMContext):
    """CallBack запрос для получения пробной подписки."""
    await state.clear()
    await call.answer(CommonMessage.LOAD_MSG_TRIAL_SUB, show_alert=False)
    async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
        url = settings.get_backend_url + settings.SERVER_PATH
        async with call.bot.http_client.get(url) as response:
            servers = await response.json()
        await state.update_data(servers=servers)
        await state.update_data(type=SubscriptionType.trial)
        await call.message.delete()
        await call.message.answer(
            CommonMessage.CHOICE_MSG_LOCATION,
            reply_markup=choice_location_kb(servers))
    await state.set_state(SubscriptionForm.location)


@router.callback_query(F.data == 'update_sub')
async def choice_type(call: CallbackQuery, state: FSMContext):
    """CallBack запрос для выбора типа, только покупка/обновление."""
    async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
        url = settings.get_backend_url + settings.SERVER_PATH
        async with call.bot.http_client.get(url) as response:
            servers = await response.json()
        await state.update_data(servers=servers)
        await call.message.delete()
        await call.message.answer(
            CommonMessage.MSG_FOR_UPDATE_SUB,
            reply_markup=choice_type_inline_kb(trial=False))
    await state.set_state(SubscriptionForm.type)


@router.callback_query(SubscriptionForm.type)
async def choice_duration(call: CallbackQuery, state: FSMContext):
    """CallBack запрос для выбора длительность, только покупка/обновление."""
    await state.update_data(type=call.data)
    async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
        await call.message.delete()
        await call.message.answer(
            CommonMessage.CHOICE_MSG_DURATION,
            reply_markup=choice_duration_kb())
    await state.set_state(SubscriptionForm.duration)


@router.callback_query(SubscriptionForm.duration)
async def choice_location(call: CallbackQuery, state: FSMContext):
    """CallBack запрос для выбора локации, только покупка/обновление."""
    await state.update_data(duration=call.data)
    data = await state.get_data()
    servers = data.get('servers')
    async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
        await call.message.delete()
        await call.message.answer(
            CommonMessage.CHOICE_MSG_LOCATION,
            reply_markup=choice_location_kb(servers))
    await state.set_state(SubscriptionForm.location)


@router.callback_query(SubscriptionForm.location)
async def choice_protocol(call: CallbackQuery, state: FSMContext):
    """CallBack запрос для выбора протокола."""
    await state.update_data(location=call.data)
    data = await state.get_data()
    servers = data.get('servers')
    async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
        await call.message.delete()
        await call.message.answer(
            CommonMessage.CHOICE_MSG_PROTOCOL,
            reply_markup=choice_protocol_kb(servers))
    await state.set_state(SubscriptionForm.protocol)


@router.callback_query(SubscriptionForm.protocol)
async def create_subscription(call: CallbackQuery, state: FSMContext):
    """Обращение к бэкенду за новой подпиской."""
    await state.update_data(protocol=call.data)
    data = await state.get_data()
    async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
        url = settings.get_backend_url + settings.SUBSCRIPTION_PATH
        payload = SubscriptionCreate(
            tg_id=call.from_user.id,
            type=data['type'],
            duration=data.get('duration', None),
            region_code=data['location'],
            protocol=data['protocol']
        )
        async with call.bot.http_client.post(
            url, json=payload.model_dump(mode='json')
        ) as response:

            if response.status != 200:
                await call.message.answer('Ошибка оформления подписки')
                return
            answer = await response.json()
    if data.get('type') == SubscriptionType.trial:
            await call.message.delete()
            await call.message.answer(
                CommonMessage.SUBSCRIPTION_INFO.format(**answer),
                reply_markup=subscription_inline_kb())
    else:
            await call.message.delete()
            # TODO: Ждем от бэкенда ссылку на оплату
            await call.message.answer(
                CommonMessage.URL_FOR_PAY.format(
                    payment_link='https://github.com/Danuuuq'),
                reply_markup=keys_inline_kb(True))
    await state.clear()


@router.callback_query(F.data == 'extension_sub')
async def extension_sub(call: CallbackQuery, state: FSMContext):
    """CallBack запрос для выбора длительности, только продление."""
    await state.update_data(type=call.data)
    async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
        await call.message.delete()
        await call.message.answer(
            CommonMessage.CHOICE_MSG_DURATION,
            reply_markup=choice_duration_kb())
    await state.set_state(SubscriptionForm.extension)


@router.callback_query(SubscriptionForm.extension)
async def extension_subscription(call: CallbackQuery, state: FSMContext):
    """Обращение к бэкенду для продления существующей подписки."""
    await state.update_data(extension=call.data)
    async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
        # TODO: обращение к бэкенду за оформлением ссылки и продлением
        # TODO: передаваться будет форма со всей информацией, но без серверов
        # TODO: Ждем от бэкенда ссылку на оплату
        await call.message.delete()
        await call.message.answer(
            CommonMessage.URL_FOR_PAY.format(
                payment_link='https://github.com/Danuuuq'),
            reply_markup=keys_inline_kb(True))
    await state.clear()
