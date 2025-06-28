from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.chat_action import ChatActionSender

from app.core.bot import bot
from app.core.config import settings
from app.forms.subscription import SubscriptionForm, SubscriptionExtensionForm
from app.keyboards.inline import (
    choice_duration_kb,
    choice_location_kb,
    choice_protocol_kb,
    choice_sub_inline_kb,
    choice_subscription_inline_kb,
    choice_type_inline_kb,
    keys_inline_kb,
    payment_kb,
    subscription_inline_kb,
)
from app.messages.common import CommonMessage
from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionType,
    SubscriptionRenew,
)

router = Router()


@router.callback_query(F.data == 'pay_subscription')
async def pay_subscription(
    call: CallbackQuery,
    state: FSMContext,
    current_user: dict,
):
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
async def choice_subscription(
    call: CallbackQuery,
    state: FSMContext,
    current_user: dict,
):
    """CallBack запрос для выбора подписки, только обновление."""
    async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
        await call.message.delete()
        await call.message.answer(
            CommonMessage.MSG_FOR_UPDATE_SUB,
            reply_markup=choice_subscription_inline_kb(current_user.get('subscription')))
    await state.set_state(SubscriptionForm.subscription)


@router.callback_query(F.data == 'new_sub')
async def new_subscription(
    call: CallbackQuery,
    state: FSMContext,
    # current_user: dict,
):
    """CallBack запрос для выбора подписки, только обновление."""
    async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
        url = settings.get_backend_url + settings.SERVER_PATH
        async with call.bot.http_client.get(url) as response:
            servers = await response.json()
        await state.update_data(servers=servers)
        await call.message.delete()
        await call.message.answer(
            CommonMessage.CHOICE_MSG_TYPE_SUB,
            reply_markup=choice_type_inline_kb(trial=False))
    await state.set_state(SubscriptionForm.type)


@router.callback_query(SubscriptionForm.subscription)
async def choice_type(call: CallbackQuery, state: FSMContext):
    """CallBack запрос для выбора типа, только покупка/обновление."""
    await state.update_data(subscription=call.data)
    async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
        url = settings.get_backend_url + settings.SERVER_PATH
        async with call.bot.http_client.get(url) as response:
            servers = await response.json()
        await state.update_data(servers=servers)
        await call.message.delete()
        await call.message.answer(
            CommonMessage.CHOICE_MSG_TYPE_SUB,
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
            sub_id=data.get('subscription', None),
            duration=data.get('duration', None),
            region_code=data['location'],
            protocol=data['protocol']
        )
        async with call.bot.http_client.post(
            url, json=payload.model_dump(mode='json')
        ) as response:

            if response.status not in (200, 201):
                await call.message.answer('Ошибка оформления подписки')
                return
            answer = await response.json()
    if data.get('type') == SubscriptionType.trial:
            lines = []
            region = answer.get('region').get('name', '❓Регион неизвестен')
            end_date = answer.get('end_date', '')[:10]
            sub_type = answer.get('type', 'неизвестно')
            lines.append(
                f'🔹 <b>Пробная подписка </b>\n'
                f'Тип: {sub_type}\n'
                f'Регион: {region}\n'
                f'До: <b>{end_date}</b>\n'
            )
            subs_info = '\n'.join(lines)
            await call.message.delete()
            await call.message.answer(
                CommonMessage.SUBSCRIPTIONS_INFO.format(subscriptions=subs_info),
                reply_markup=subscription_inline_kb())
    else:
            await call.message.delete()
            await call.message.answer(
                CommonMessage.URL_FOR_PAY.format(**answer),
                reply_markup=payment_kb(answer.get('url')))
    await state.clear()


@router.callback_query(F.data == 'renew_sub')
async def renew_sub(
    call: CallbackQuery,
    state: FSMContext,
    current_user: dict,
):
    """CallBack запрос для выбора подписки, только продление."""
    async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
        subscription = current_user.get('subscription')
        await call.message.delete()
        if not subscription:
            await call.message.answer("У тебя нет активных подписок для продления.")
        await call.message.answer(
            CommonMessage.MSG_FOR_RENEW_SUB,
            reply_markup=choice_subscription_inline_kb(subscription))
        if (len(subscription) == 1 and
            subscription[-1].get('type') == SubscriptionType.trial):
            await state.set_state(SubscriptionExtensionForm.type)
        else:
            await state.set_state(SubscriptionExtensionForm.sub_id)


@router.callback_query(SubscriptionExtensionForm.type)
async def type_renew_sub(call: CallbackQuery, state: FSMContext):
    """CallBack запрос для выбора длительности, только продление."""
    await state.update_data(sub_id=call.data)
    async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
        await call.message.delete()
        await call.message.answer(
            CommonMessage.CHOICE_MSG_TYPE_SUB,
            reply_markup=choice_type_inline_kb())
    await state.set_state(SubscriptionExtensionForm.sub_id)


@router.callback_query(SubscriptionExtensionForm.sub_id)
async def extension_sub(call: CallbackQuery, state: FSMContext):
    """CallBack запрос для выбора длительности, только продление."""
    async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
        data = await state.get_data()
        if data.get('sub_id'):
            await state.update_data(type=call.data)
        else:
            await state.update_data(sub_id=call.data)
        await call.message.delete()
        await call.message.answer(
            CommonMessage.CHOICE_MSG_DURATION,
            reply_markup=choice_duration_kb())
    await state.set_state(SubscriptionExtensionForm.extension)


@router.callback_query(SubscriptionExtensionForm.extension)
async def extension_subscription(call: CallbackQuery, state: FSMContext):
    """Обращение к бэкенду для продления существующей подписки."""
    await state.update_data(extension=call.data)
    data = await state.get_data()
    async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
        url = f'{settings.get_backend_url}{settings.SUBSCRIPTION_PATH}'
        payload = SubscriptionRenew(
            tg_id=call.from_user.id,
            sub_id=data.get('sub_id'),
            duration=data.get('extension'),
            type=data.get('type')
        )
        async with call.bot.http_client.patch(
            url, json=payload.model_dump(mode='json')
        ) as response:
            if response.status not in (200, 201):
                await call.message.answer('Ошибка оформления подписки')
                return
            answer = await response.json()
        await call.message.delete()
        await call.message.answer(
            CommonMessage.URL_FOR_PAY_RENEW.format(**answer),
            reply_markup=payment_kb(answer.get('url')))
    await state.clear()
