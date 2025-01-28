import sys
import traceback

from loguru import logger
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger.remove()
logger.add(sys.stdout, colorize=True, format="<green>{time}</green> <level>{message}</level> - {extra}")


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None and isinstance(exc, APIException):
        logger.bind(error_response=str(response.data)).error("Ошибка from handler")
        return response

    exc_type, exc_value, exc_tb = sys.exc_info()

    tb_lines = traceback.format_exception(exc_type, exc_value, exc_tb)
    tb_summary = [line.strip() for line in tb_lines[:5]]

    custom_response = {
        "error": str(exc),
        "details": {
            "type": str(exc_type),
            "value": str(exc_value),
            "traceback": tb_summary
        },
    }


    logger.bind(error_response=custom_response).error("Ошибка from handler")

    return Response(custom_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)