import time
from loguru import logger
import functools


def chek_time(func):
    """Декоратор, который принимает функцию,
       считает затраченное время на инициализацию кода и выводит ошибки,
       если они имеются """
    error_print = '\033[91m'

    @functools.wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            finish = (end-start)
            logger.info(f"Запускаю функцию {func.__name__}.")
            logger.info(f"Время затраченное на инициализацию кода составляет: {round(finish,2)} секунды.")
            logger.info(f"Функция {func.__name__} успешно отработала.")
            logger.info("="*100)
            return result
        except Exception as exc:
            logger.info(error_print+f'Ошибка, функция {func.__name__} не завершена: {exc}'+error_print)
            logger.info("="*100)
    return wrapper_func
