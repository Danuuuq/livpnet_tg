from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.utils.chat_action import ChatActionSender
from tempfile import NamedTemporaryFile

from app.core.bot import bot
from app.forms.subscription import SupportForm
from app.keyboards.inline import (
    device_inline_kb,
    keys_inline_kb,
    protocol_inline_kb,
    subscription_inline_kb)
from app.messages.common import CommonMessage
from .examples_data import response

router = Router()


@router.callback_query(F.data == 'get_subscription')
async def get_subscription_user(call: CallbackQuery, current_user: dict):
    """CallBack запрос для получения подписки пользователя."""
    await call.answer(CommonMessage.LOAD_MSG_SUB, show_alert=False)
    # TODO: Подписка будет в current_user
    subscription = current_user.get('subscription')
    if subscription:
        await call.message.delete()
        await call.message.answer(
            CommonMessage.SUBSCRIPTION_INFO.format(**subscription),
            reply_markup=subscription_inline_kb())
    else:
        await call.message.delete()
        await call.message.answer(
            CommonMessage.SUBSCRIPTION_WELCOME,
            reply_markup=subscription_inline_kb(trial=True))


@router.callback_query(F.data == 'get_ref_url')
async def get_ref_url(call: CallbackQuery, current_user: dict):
    """CallBack запрос для получения реферальной ссылки."""
    await call.answer(CommonMessage.LOAD_MSG_REF, show_alert=False)
    # TODO: Выдавать информацию пользователю о его текущем состоянии бонусов
    # TODO: Сделать запрос к бекенду по всем рефералкам
    async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
        await call.message.delete()
        await call.message.answer(CommonMessage.REFERRAL_MESSAGE.format(
            user_id=call.from_user.id),
                                  reply_markup=keys_inline_kb(True))


@router.callback_query(F.data == 'get_price')
async def get_price(call: CallbackQuery):
    """CallBack запрос для получения информации по стоимости."""
    await call.answer(CommonMessage.LOAD_MSG_PRICE, show_alert=False)
    async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
        await call.message.delete()
        await call.message.answer(CommonMessage.PRICE_MESSAGE,
                                  reply_markup=keys_inline_kb(False))


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
            # TODO: Обращение к бэкенду за QR кодом или ovpn файлами
            # TODO: Должно содержать content, filename, type
            if response["type"] == "ovpn":
                with NamedTemporaryFile("w+", delete=False,
                                        suffix=".ovpn") as f:
                    f.write(response['content'])
                    temp_path = f.name
                await call.message.delete()
                await call.message.answer_document(
                    document=FSInputFile(temp_path,
                                         filename=response['filename']),
                    caption=CommonMessage.MSG_FOR_OVPN,
                    reply_markup=keys_inline_kb(True))
            elif response["type"] == "qr":
                await call.message.delete()
                await call.message.answer_photo(
                    photo=response.get('image'),
                    caption=CommonMessage.MSG_FOR_VLESS.format(
                        url=response.get('url')),
                    reply_markup=keys_inline_kb(True))
    else:
        await call.message.delete()
        await call.message.answer(
                CommonMessage.MSG_WITHOUT_SUB,
                reply_markup=keys_inline_kb(False))
