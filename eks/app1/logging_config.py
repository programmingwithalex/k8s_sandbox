from loguru import logger

logger.add("app1/app1_service.log", rotation="1 week", level="INFO")
