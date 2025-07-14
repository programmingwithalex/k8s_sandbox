from loguru import logger

logger.add("auth/auth_service.log", rotation="1 week", level="INFO")
