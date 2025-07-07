from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.chat_action import ChatActionSender

from app.core.bot import bot
from app.core.config import settings
from app.forms.subscription import SupportForm
from app.keyboards.inline import (
    device_inline_kb,
    keys_inline_kb,
    keys_referral_kb,
    protocol_inline_kb,
    subscription_inline_kb,
)
from app.messages.common import CommonMessage

router = Router()


@router.callback_query(F.data == 'get_subscription')
async def get_subscription_user(call: CallbackQuery, current_user: dict):
    """CallBack запрос для получения подписки пользователя."""
    await call.answer(CommonMessage.LOAD_MSG_SUB, show_alert=False)
    subscriptions = current_user.get('subscription', None)
    if subscriptions:
        await call.message.delete()
        await call.message.answer(
            CommonMessage.format_start_message(
                name=call.from_user.first_name,
                main_menu=False,
                subscriptions=subscriptions,
            ),
            reply_markup=subscription_inline_kb())
    else:
        await call.message.delete()
        await call.message.answer(
            CommonMessage.format_start_message(
                name=call.from_user.first_name,
                main_menu=False,
            ),
            reply_markup=subscription_inline_kb(trial=True))


@router.callback_query(F.data == 'get_ref_url')
async def get_ref_url(call: CallbackQuery):
    """CallBack запрос для получения реферальной ссылки."""
    await call.answer(CommonMessage.LOAD_MSG_REF, show_alert=False)
    async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
        url = (settings.get_backend_url +
               settings.PAYMENT_PATH +
               str(call.from_user.id))
        async with call.bot.http_client.get(url) as response:
            if response.status != 200:
                await call.message.answer('Ошибка запроса состояния бонусов')
                return
            answer = await response.json()
        await call.message.delete()
        await call.message.answer(
            CommonMessage.REFERRAL_INFO_MESSAGE.format(
                **answer,
            ),
            reply_markup=keys_referral_kb())


@router.callback_query(F.data == 'get_price')
async def get_price(call: CallbackQuery):
    """CallBack запрос для получения информации по стоимости."""
    await call.answer(CommonMessage.LOAD_MSG_PRICE, show_alert=False)
    async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
        url = (settings.get_backend_url +
                settings.SUBSCRIPTION_PATH +
                settings.PRICE_PATH)
        async with call.bot.http_client.get(url) as response:
            if response.status != 200:
                await call.message.answer('Ошибка запроса цены на ВПН')
                return
            answer = await response.json()
        await call.message.delete()
        await call.message.answer(CommonMessage.format_price_message(answer),
                                  reply_markup=keys_inline_kb())


@router.callback_query(F.data == 'get_help')
async def get_help(call: CallbackQuery, state: FSMContext):
    """CallBack запрос для получения инструкций."""
    await call.answer(CommonMessage.LOAD_MSG_FAQ, show_alert=False)
    async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
        await call.message.delete()
        await call.message.answer(CommonMessage.CHOICE_MSG_PROTOCOL,
                                  reply_markup=protocol_inline_kb())
    await state.set_state(SupportForm.protocol)


@router.callback_query(SupportForm.protocol)
async def choice_device(call: CallbackQuery, state: FSMContext):
    """CallBack запрос для выбора устройства."""
    await state.update_data(protocol=call.data)
    data = await state.get_data()
    protocol = data.get('protocol')
    await call.answer(CommonMessage.LOAD_MSG_FAQ, show_alert=False)
    await call.message.delete()
    await call.message.answer(CommonMessage.CHOICE_MSG_FAQ_DEVICE,
                              reply_markup=device_inline_kb(protocol))


# TODO: Пересылать сообщения администраторам или в бот где подключен ИИ
@router.callback_query(F.data == 'get_support')
async def get_support(call: CallbackQuery, state: FSMContext,
                      current_user: dict):
    """CallBack запрос для обращения в поддержку."""
    await call.answer(CommonMessage.LOAD_MSG_SUPPORT, show_alert=False)
    await call.message.delete()
    await call.message.answer(CommonMessage.MSG_FOR_TROUBLE,
                              f'{call.from_user.first_name}')


@router.callback_query(F.data == 'get_certificate')
async def get_certificate(call: CallbackQuery, current_user: dict):
    """CallBack запрос для получения ключей или сертификатов."""
    assert call.message is not None
    assert isinstance(call.message, Message)
    await call.answer(CommonMessage.LOAD_MSG_KEYS, show_alert=False)
    if current_user.get('subscription'):
        async with ChatActionSender.typing(bot=bot,
                                           chat_id=call.message.chat.id):
            url = (settings.get_backend_url +
                   settings.SUBSCRIPTION_PATH +
                   str(call.from_user.id))
            async with call.bot.http_client.get(url) as response:
                if response.status != 200:
                    await call.message.answer('Ошибка запроса сертификатов')
                    return
                answer = await response.json()
            await call.message.delete()
            await call.message.answer(
                CommonMessage.MSG_FOR_OVPN,
                reply_markup=keys_inline_kb(answer))
    else:
        await call.message.delete()
        await call.message.answer(
                CommonMessage.MSG_WITHOUT_SUB,
                reply_markup=keys_inline_kb())
