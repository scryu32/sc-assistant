import logging
import functools

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

file_handler = logging.FileHandler("log.txt", encoding="utf-8")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def log_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"함수 {func.__name__} 실행 시작 | args: {args}, kwargs: {kwargs}")
        result = func(*args, **kwargs)
        logger.info(f"함수 {func.__name__} 실행 완료 | 반환값: {result}")
        return result
    return wrapper