class SettingFieldDB:
    DEFAULT_FOR_COUNT = 0
    DEFAULT_MAX_CERT = 10
    DEFAULT_ACTIVE_SRV = False
    DEFAULT_ACTIVE_SUB = False
    MAX_LENGTH_CODE_REGION = 2
    MAX_LENGTH_NAME = 64
    MAX_LENGTH_IP = 16
    MAX_LENGTH_PROTOCOL = 16
    MAX_LENGTH_FILENAME = 64
    MAX_LENGTH_TYPE_SUB = 64


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
