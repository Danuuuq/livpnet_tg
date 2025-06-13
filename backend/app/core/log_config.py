import json
import os
import sys
import traceback
from datetime import datetime
from functools import wraps
from pathlib import Path
from types import FunctionType
from typing import Any, Optional

from fastapi.encoders import jsonable_encoder
from loguru import logger
from pydantic import BaseModel

from app.core.variables import SettingLogging
from app.schemas.user import UserBase


def setup_logger() -> Any:
    """Настройка логгера с использованием loguru."""
    app_logger = logger.bind(app='vink')

    for logger_name in SettingLogging.SUPPRESSED_LOGGERS:
        app_logger.disable(logger_name)

    os.makedirs(SettingLogging.LOG_DIR, exist_ok=True)

    log_file = Path(SettingLogging.LOG_DIR) / \
        f'app_{datetime.now().strftime(SettingLogging.LOG_DATE_FORMAT)}.log'
    app_logger.add(
        sink=log_file,
        rotation=SettingLogging.LOG_ROTATION,
        retention=SettingLogging.LOG_RETENTION,
        encoding=SettingLogging.LOG_FILE_ENCODING,
        format=SettingLogging.LOG_FORMAT,
        level=SettingLogging.LOG_LEVEL,
        compression=SettingLogging.LOG_COMPRESSION,
        enqueue=False,
    )
    app_logger.configure(extra={'endpoint': 'system', 'method': 'N/A'})
    return app_logger


def log_db_action(
        action_name: str = 'DB Action',
        private_data: bool = False) -> FunctionType:
    """Логирование действий в методах классов service."""
    def decorator(func: FunctionType) -> FunctionType:
        @wraps(func)
        async def wrapper(*args: tuple, **kwargs: dict) -> FunctionType:
            """Запись логов с данными из класса."""
            user_self = getattr(args[0], 'user', None)
            if args:
                user_args = [us for us in args if isinstance(us, UserBase)]
            user = user_self or user_args[0] or None
            tg_id_user = getattr(user, 'telegram_id', 'Anonymous')

            if private_data:
                obj_data = 'NO DATA'
            else:
                obj_data = [
                    obj.model_dump() for obj in args if isinstance(
                        obj, BaseModel)]
                obj_data = obj_data[0] if obj_data else None
                obj_data = json.dumps(jsonable_encoder(
                    obj_data), ensure_ascii=False)
            try:
                result = await func(*args, **kwargs)
                app_logger.opt(depth=1).info(
                    f'{action_name} SUCCESS by {tg_id_user} | '
                    f'Data: {obj_data} | ',
                )
                return result
            except Exception as error:
                exc_tb = sys.exc_info()[-1]
                frame = traceback.extract_tb(
                    exc_tb)[-1] if exc_tb else None
                app_logger.opt(depth=1).error(
                    f'{action_name} FAILED by {tg_id_user} | '
                    f'Data: {obj_data} | '
                    f'Error: {error} | '
                    f'Location: {frame.filename if frame else 'unknown'} | '
                    f'String: {frame.lineno if frame else 'unknown'} | '
                    f'Function: {frame.name if frame else 'unknown'}',
                )
                raise
        return wrapper
    return decorator


def log_action_status(
    error: Optional[Exception] = None,
    action_name: str = 'Action',
    message: str = '',
) -> None:
    """Логирует ошибку при выполнении произвольного действия."""
    if error is not None:
        exc_tb = sys.exc_info()[-1]
        last_frame = traceback.extract_tb(exc_tb)[-1] if exc_tb else None

        app_logger.opt(depth=1).error(
            f'{action_name} FAILED | '
            f'Error: {str(error)} | '
            f'Location: {last_frame.filename if last_frame else 'unknown'} | '
            f'String: {last_frame.lineno if last_frame else 'unknown'} | '
            f'Function: {last_frame.name if last_frame else 'unknown'}',
        )
    else:
        app_logger.info(message)


app_logger = setup_logger()
