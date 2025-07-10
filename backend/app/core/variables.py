class SettingFieldDB:
    DEFAULT_FOR_COUNT = 0
    DEFAULT_MAX_CERT = 20
    DEFAULT_ACTIVE_SRV = False
    DEFAULT_ACTIVE_SUB = False
    DEFAULT_GIVEN_BONUS = False
    DEFAULT_BONUS = 100.00
    MAX_LENGTH_CODE_REGION = 2
    MAX_LENGTH_NAME = 64
    MAX_LENGTH_NAME_PROVIDER = 64
    MAX_LENGTH_IP = 16
    MAX_LENGTH_ID_OPERATION = 128
    MAX_LENGTH_PROTOCOL = 16
    MAX_LENGTH_FILENAME = 1024
    MAX_LENGTH_TYPE_SUB = 64
    MAX_PRECISION_NUMERIC = 10
    MAX_SCALE_NUMERIC = 2
    LENGTH_REGION_CODE = 2
    DEFAULT_CURRENCY = 'RUB'


class SettingLogging:
    SUPPRESSED_LOGGERS: list[str] = ['uvicorn', 'uvicorn.error',
                                     'fastapi', 'uvicorn.access']
    LOG_DIR: str = 'logs'
    LOG_FORMAT: str = (
        '{time:HH:mm:ss} | {level} | {extra[endpoint]} | {message}')
    LOG_DATE_FORMAT: str = '%Y-%m-%d'
    LOG_FILE_ENCODING: str = 'utf-8'
    LOG_ROTATION: str = '00:00'
    LOG_RETENTION: str = '7 days'
    LOG_COMPRESSION: str = 'zip'
    LOG_LEVEL: str = 'DEBUG'


class SettingServers:
    API_CERT_HOOK: str = 'certificates'
    API_CHECK_HEALTH: str = 'health'
    API_OK_HEALTH: str = 'ok'
    URL_TGBOT: str = 'https://t.me/livpnet_bot'
    YOOKASSA_NAME: str = 'YooKassa'
    DEFAULT_CURRENCY = 'RUB'
    DEFAULT_TYPE_CONFIRM = 'redirect'
