from loguru import logger

logger.add("app2/app2_service.log", rotation="1 week", level="INFO")
