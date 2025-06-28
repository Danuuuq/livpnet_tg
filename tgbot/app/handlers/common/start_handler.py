from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.keyboards.inline import main_inline_kb
from app.messages.common import CommonMessage

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, current_user: dict):
    """Команда для запуска бота."""
    await state.clear()
    subscriptions = current_user.get('subscription')
    if subscriptions:
        lines = []
        for idx, sub in enumerate(subscriptions, start=1):
            region = sub.get('region').get('name', '❓Регион неизвестен')
            end_date = sub.get('end_date', '')[:10]
            sub_type = sub.get('type', 'неизвестно')
            lines.append(
                f'🔹 <b>Подписка №{idx}</b>\n'
                f'Тип: {sub_type}\n'
                f'Регион: {region}\n'
                f'До: <b>{end_date}</b>\n'
            )

        subs_info = '\n'.join(lines)
        await message.answer(
            CommonMessage.HELLO_FOR_CLIENT.format(
                name=message.from_user.first_name,
                subscriptions_info=subs_info,
            ),
            reply_markup=main_inline_kb()
        )
    else:
        await message.answer(
            CommonMessage.HELLO_WITHOUT_SUB.format(
                name=message.from_user.first_name),
            reply_markup=main_inline_kb())


@router.callback_query(F.data == 'main_menu')
async def callback_start(call: CallbackQuery, state: FSMContext,
                         current_user: dict):
    """Возвращение в главное меню."""
    await state.clear()
    subscriptions = current_user.get('subscription')
    if subscriptions:
        lines = []
        for idx, sub in enumerate(subscriptions, start=1):
            region = sub.get('region').get('name', '❓Регион неизвестен')
            end_date = sub.get('end_date', '')[:10]
            sub_type = sub.get('type', 'неизвестно')
            lines.append(
                f'🔹 <b>Подписка №{idx}</b>\n'
                f'Тип: {sub_type}\n'
                f'Регион: {region}\n'
                f'До: <b>{end_date}</b>\n'
            )

        subs_info = '\n'.join(lines)
        await call.message.delete()
        await call.message.answer(
            CommonMessage.HELLO_FOR_CLIENT.format(
                name=call.from_user.first_name,
                subscriptions_info=subs_info,
            ),
            reply_markup=main_inline_kb()
        )
        # subscription = subscription.pop()
        # await call.message.delete()
        # await call.message.answer(
        #     CommonMessage.HELLO_FOR_CLIENT.format(
        #         name=call.from_user.first_name,
        #         end_data=subscription.get('end_date')),
        #     reply_markup=main_inline_kb())
    else:
        await call.message.delete()
        await call.message.answer(
            CommonMessage.HELLO_WITHOUT_SUB.format(
                name=call.from_user.first_name),
            reply_markup=main_inline_kb())
