import os
import json
import requests
import allure
from dotenv import load_dotenv
from typing import Tuple, Dict, Any, Optional
from Helpers.Allure_helper import attach_json


class ProjectYouGile:
    def __init__(self) -> None:
        """
        Инициализирует экземпляр класса,
        загружая параметры из переменных окружения.
        """
        load_dotenv()
        self.url: Optional[str] = os.getenv('URL')

    @allure.step("Получение ID компании по логину и паролю")
    def get_id_company(
            self, login: str, password: str) -> Tuple[int, Dict[str, Any]]:
        """
        Авторизуется и получает ID компании через POST /auth/companies.

        Args:
            login (str): логин пользователя.
            password (str): пароль пользователя.
        Returns:
            Tuple[int, Dict[str, Any]]: кортеж из двух элементов:
                - int: HTTP‑статус‑код ответа.
                - dict: тело ответа API в формате JSON.
        """
        url = f'{self.url}/auth/companies'
        payload_data = {
            "login": login,
            "password": password
        }

        payload_str = json.dumps(payload_data)
        headers = {
            'Content-Type': 'application/json'
        }

        with allure.step(f"Отправка POST‑запроса к {url}"):
            attach_json(payload_data, name="Payload (POST /auth/companies)")
            response = requests.request(
                "POST",
                url,
                headers=headers,
                data=payload_str,
                timeout=20
            )

        status_code = response.status_code
        response_body = response.json()

        with allure.step(f"Получен ответ: статус {status_code}"):
            attach_json(response_body, name="Response Body")

        return status_code, response_body

    @allure.step("Создание нового проекта: title={title}, user_id={user_id}")
    def create_new_project(
            self, title: str, user_id: str) -> Tuple[int, Dict[str, Any]]:
        """
        Создаёт новый проект через POST /projects.

        Args:
            title (str): название проекта.
            user_id (str): ID пользователя-администратора проекта.
        Returns:
            Tuple[int, Dict[str, Any]]: кортеж из двух элементов:
                - int: HTTP‑статус‑код ответа.
                - dict: тело ответа API в формате JSON.
        """

        url = f'{self.url}/projects'
        key = os.getenv('API_KEY')
        token = f'Bearer {key}'

        payload_data = {
            "title": title,
            "users": {user_id: 'admin'}
        }

        payload_str = json.dumps(payload_data)

        headers = {
            'Content-Type': 'application/json',
            'Authorization': token
        }

        with allure.step(f"Отправка POST‑запроса к {url}"):
            attach_json(payload_data, name="Payload (POST /projects)")
            response = requests.request(
                "POST",
                url,
                headers=headers,
                data=payload_str,
                timeout=20
            )

        status_code = response.status_code
        response_body = response.json()

        with allure.step(f"Получен ответ: статус {status_code}"):
            attach_json(response_body, name="Response Body")

        return status_code, response_body

    @allure.step("Обновление проекта: id={id_project}, new_title={new_title}")
    def update_project(
            self, id_project: str,
            new_title: str, key: str) -> Tuple[int, Dict[str, Any]]:
        """
        Обновляет название проекта через PUT /projects/{id_project}.

        Args:
            id_project (str): ID обновляемого проекта.
            new_title (str): новое название проекта.
            key (str): API‑ключ для авторизации.
        Returns:
            Tuple[int, Dict[str, Any]]: кортеж из двух элементов:
                - int: HTTP‑статус‑код ответа.
                - dict: тело ответа API в формате JSON.
        """
        url = f'{self.url}/projects/{id_project}'
        token = f'Bearer {key}'

        payload_data = {
            'title': new_title
        }

        payload_str = json.dumps(payload_data)

        headers = {
            'Content-Type': 'application/json',
            'Authorization': token
        }

        with allure.step(f"Отправка PUT‑запроса к {url}"):
            attach_json(payload_data, name="Payload (PUT /projects/{id})")
            response = requests.request(
                "PUT",
                url,
                headers=headers,
                data=payload_str,
                timeout=20
            )

        status_code = response.status_code
        response_body = response.json()

        with allure.step(f"Получен ответ: статус {status_code}"):
            attach_json(response_body, name="Response Body")

        return status_code, response_body

    @allure.step("Получение проекта по ID: {id_project}")
    def get_project_on_id(self, id_project: str) -> Tuple[int, Dict[str, Any]]:
        """
        Получает данные проекта по его ID через GET /projects/{id_project}.

        Args:
            id_project (str): ID запрашиваемого проекта.
        Returns:
            Tuple[int, Dict[str, Any]]: кортеж из двух элементов:
                - int: HTTP‑статус‑код ответа.
                - dict: тело ответа API в формате JSON.
        """
        url = f'{self.url}/projects/{id_project}'
        key = os.getenv("API_KEY")
        token = f'Bearer {key}'

        headers = {
            'Content-Type': 'application/json',
            'Authorization': token
        }

        with allure.step(f"Отправка GET‑запроса к {url}"):
            response = requests.request(
                "GET",
                url,
                headers=headers,
                timeout=20
            )

        status_code = response.status_code
        response_body = response.json()

        with allure.step(f"Получен ответ: статус {status_code}"):
            attach_json(response_body, name="Response Body")

        return status_code, response_body

    @allure.step("Получение списка всех проектов")
    def get_all_projects(self) -> Tuple[int, Dict[str, Any]]:
        """
        Получает список всех проектов через GET /projects.

        Returns:
            Tuple[int, Dict[str, Any]]: кортеж из двух элементов:
                - int: HTTP‑статус‑код ответа.
                - dict: тело ответа API в формате JSON.
        """
        url = f'{self.url}/projects'
        key = os.getenv("API_KEY")
        token = f'Bearer {key}'

        headers = {
            'Content-Type': 'application/json',
            'Authorization': token
        }

        with allure.step(f"Отправка GET‑запроса к {url}"):
            response = requests.request(
                "GET",
                url,
                headers=headers,
                timeout=20
            )

        status_code = response.status_code
        response_body = response.json()

        with allure.step(f"Получен ответ: статус {status_code}"):
            attach_json(response_body, name="Response Body")

        return status_code, response_body

    @allure.step("Удаление проекта по ID: {id_project}")
    def delete_project(self, id_project: str) -> Tuple[int, Dict[str, Any]]:
        """
        Удаляет проект (soft delete) через
        PUT /projects/{id_project} с полем deleted=True.

        Args:
            id_project (str): ID удаляемого проекта.
        Returns:
            Tuple[int, Dict[str, Any]]: кортеж из двух элементов:
                - int: HTTP‑статус‑код ответа.
                - dict: тело ответа API в формате JSON.
        """
        url = f'{self.url}/projects/{id_project}'
        key = os.getenv('API_KEY')
        token = f'Bearer {key}'

        payload_data = {
            "deleted": True
        }

        payload_str = json.dumps(payload_data)

        headers = {
            'Content-Type': 'application/json',
            'Authorization': token
        }

        with allure.step(f"Отправка PUT‑запроса к {url}"):
            attach_json(payload_data, name="Payload (PUT /projects/{id})")
            response = requests.request(
                "PUT",
                url,
                headers=headers,
                data=payload_str,
                timeout=20
            )

        status_code = response.status_code
        response_body = response.json()

        with allure.step(f"Получен ответ: статус {status_code}"):
            attach_json(response_body, name="Response Body")

        return status_code, response_body

    @allure.step("Получение списка сотрудников (users) по API-key")
    def get_all_users(self, key: str) -> Tuple [int, Dict[str, Any]]:
        """
        Получает список users через GET /users.

        Args:
        key (str): API-key пользователя.
        Returns:
        Tuple[int, Dict[str, Any]]: кортеж из двух элементов:
        - int: HTTP‑статус‑код ответа.
        - dict: тело ответа API в формате JSON.
        """
        url = f'{self.url}/users'
        token = f'Bearer {key}'

        headers = {
            'Content-Type': 'application/json',
            'Authorization': token
        }

        with allure.step(f"Отправка GET‑запроса к {url}"):
            response = requests.request(
            "GET",
            url,
            headers=headers,
            timeout=20
        )

        status_code = response.status_code
        response_body = response.json()

        with allure.step(f"Получен ответ: статус {status_code}"):
            attach_json(response_body, name="Response Body")

        return status_code, response_body

    @allure.step("Получение API-key по логину и паролю")
    def get_api_key(
            self,
            login: str,
            password: str,
            company_id: str) -> Tuple[int, Dict[str, Any]]:
        """
        Авторизуется и получает API-key через POST /auth/keys.

        Args:
        login (str): логин пользователя.
        password (str): пароль пользователя.
        company_id (str): id компании.
        Returns:
        Tuple[int, Dict[str, Any]]: кортеж из двух элементов:
        - int: HTTP‑статус‑код ответа.
        - dict: тело ответа API в формате JSON.
        """

        url = f'{self.url}/auth/keys'
        payload_data = {
            "login": login,
            "password": password,
            "companyId": company_id,
        }

        with allure.step(f"Отправка POST-запроса к {url}"):
            attach_json(payload_data, name="Payload (POST /api-v2/auth/keys)")

        response = requests.post(url, json=payload_data, timeout=20)
        status_code = response.status_code
        resp = response.json()

        with allure.step(f"Получен ответ: статус {status_code}"):
            attach_json(resp, name="Response Body")

        return status_code, resp
