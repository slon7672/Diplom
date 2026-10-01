import json
import allure
from allure import attachment_type


def attach_json(data: dict | list, name: str) -> None:
    """
    Прикрепляет JSON к отчёту Allure с корректной кодировкой кириллицы.

    Args:
        data: словарь или список (Python-объект),
        который нужно перекодировать.
        name: имя attach-мента в отчёте.
    """
    allure.attach(
        json.dumps(data, ensure_ascii=False, indent=2),
        name=name,
        attachment_type=attachment_type.JSON,
    )
