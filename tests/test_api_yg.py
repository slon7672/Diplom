import os
import pytest
import allure
from Pages.API_YGP import ProjectYouGile
from dotenv import load_dotenv
from typing import Dict, Any


load_dotenv()
api = ProjectYouGile()


@pytest.fixture
def project() -> Dict[str, Any]:
    """
    Создаёт проект для использования в тестах и удаляет его после.
    Returns:
        Dict[str, Any]: словарь с данными созданного проекта
            (содержит поле "id").
    """
    title = os.getenv("TITLE")
    user_id = os.getenv("USER")
    status, resp = api.create_new_project(title, user_id)
    assert status == 201, "Не удалось создать проект для теста"

    yield resp

    # Очистка
    if "id" in resp:
        api.delete_project(resp["id"])


@allure.feature("Авторизация")
@allure.story("Получение ID компании: позитивный сценарий")
@pytest.mark.aut
@pytest.mark.positive
def test_get_id_company() -> None:
    """
    Проверяет получение ID компании при корректных логине и пароле.

    Returns:
        None
    """
    login = os.getenv("LOG")
    password = os.getenv("PASS")

    with allure.step("Отправка запроса на получение ID компании"):
        status, resp = api.get_id_company(login, password)

    with allure.step("Проверка статус-кода"):
        assert status == 200, f"Ожидался статус 200, но получен {status}"

    with allure.step("Проверка структуры ответа: поля paging и content"):
        assert "paging" in resp, "Отсутствует поле paging"
        assert "content" in resp, "Отсутствует поле content"
        assert isinstance(resp["content"], list), (
            "Поле content должно быть списком")
        assert len(resp["content"]) > 0, "Список content пуст"

    with allure.step("Проверка полей компании"):
        company = resp["content"][0]
        assert "id" in company, "У компании нет поля id"
        assert "name" in company, "У компании нет поля name"
        assert "isAdmin" in company, "У компании нет поля isAdmin"

        id_company = company["id"]
        name_company = company["name"]
        is_admin = company["isAdmin"]

    with allure.step("Проверка значений полей компании"):
        assert id_company is not None
        assert name_company is not None
        assert is_admin is True


@allure.feature("Авторизация")
@allure.story("Получение ID компании: негативный сценарий (неверные данные)")
@pytest.mark.aut
@pytest.mark.negative
def test_get_id_company_negative_aut() -> None:
    """
    Проверяет получение ID компании при неверных логине и пароле.
    Ожидается статус 401 и сообщение об ошибке.

    Returns:
        None
    """
    login = os.getenv("F_LOG")
    password = os.getenv("F_PASS")
    s_code = int(os.getenv("STATUS_CODE_1"))
    note = os.getenv("MESSAGE")
    misstep = os.getenv("ERROR")

    with allure.step("Отправка запроса с неверными логином и паролем"):
        status, resp = api.get_id_company(login, password)

    with allure.step("Проверка статус-кода"):
        assert status == 401, f"Ожидался статус 401, но получен {status}"

    with allure.step("Проверка структуры ответа об ошибке"):
        assert "statusCode" in resp, "Отсутствует поле statusCode"
        assert "message" in resp, "Отсутствует поле message"
        assert "error" in resp, "Отсутствует поле error"

        status_code = resp["statusCode"]
        message = resp["message"]
        error = resp["error"]

    with allure.step("Проверка значений полей ошибки"):
        assert status_code == s_code, (
            f"Ожидался {s_code}, но получен {status_code}")
        assert message == note, f"Ожидался {note}, но получен {message}"
        assert error == misstep, f"Ожидался {misstep}, но получен {error}"


@allure.feature("Проекты")
@allure.story("Создание нового проекта: позитивный сценарий")
@pytest.mark.positive
@pytest.mark.creation
def test_create_new_project() -> None:
    """
    Проверяет успешное создание проекта: статус 201 и корректный ID в ответе.
    Также проверяет удаление проекта и совпадение ID в ответе на удаление.

    Returns:
        None
    """
    title = os.getenv("TITLE")
    user_id = os.getenv("USER")

    with allure.step("Отправка запроса на создание проекта"):
        status, resp = api.create_new_project(title, user_id)

    with allure.step("Проверка статус-кода и наличия поля 'id'"):
        assert status == 201, f"Ожидался статус 201, но получен {status}"
        assert "id" in resp, "В ответе отсутствует поле 'id'"

    project_id = resp["id"]

    with allure.step("Валидация значения поля 'id'"):
        assert project_id is not None, "Поле 'id' равно None"
        assert isinstance(project_id, str), (
            f"Поле 'id' должно быть строкой, а получено: {type(project_id)}")
        assert len(project_id) > 0, "Поле 'id' пустое"

    with allure.step("Удаление созданного проекта"):
        status_code, response = api.delete_project(project_id)

    with allure.step("Проверка ответа на удаление"):
        assert status_code == 200, (
            f"Ожидался статус 200, но получен {status_code}")

    delete_id = response["id"]
    with allure.step("Проверка совпадения ID при удалении"):
        assert delete_id == project_id, (
            f"Удалялся {project_id}, но в ответе пришёл {delete_id}")


@allure.feature("Проекты")
@allure.story("Попытка создания дубликата проекта: негативный сценарий")
@pytest.mark.negative
@pytest.mark.duplicate
@pytest.mark.creation
def test_create_duble_project_negative(project: Dict[str, Any]) -> None:
    """
    Проверяет, что API не позволяет создать второй проект с тем же названием.
    Первый проект берётся из фикстуры,
    второй создаётся вручную и сразу удаляется.

    Args:
        project (Dict[str, Any]): данные первого проекта из фикстуры.
    Returns:
        None
    """
    with allure.step("Валидация данных первого проекта из фикстуры"):
        assert "id" in project, "В ответе фикстуры отсутствует поле 'id'"
        project_id_1 = project["id"]
        assert project_id_1 is not None, "Поле 'id' первого проекта равно None"
        assert isinstance(project_id_1, str), (
            f"Поле 'id' первого проекта должно быть строкой,"
            f"а получено: {type(project_id_1)}")
        assert len(project_id_1) > 0, "Поле 'id' первого проекта пустое"

    title = os.getenv("TITLE")
    user_id = os.getenv("USER")

    with allure.step("Попытка создать второй проект с тем же названием"):
        st, response = api.create_new_project(title, user_id)

    # Сохраняем ID для удаления (может быть None, если API не создал дубль)
    project_id_2 = response.get("id")

    with allure.step("Получение списка всех проектов для проверки дублей"):
        status_code, ress = api.get_all_projects()

    with allure.step("Проверка статуса списка проектов"):
        assert status_code == 200, (
            f"Ожидался статус 200, но получен {status_code}")
        assert isinstance(ress["content"], list), (
            "Поле content должно быть списком")

    projects = ress["content"]
    same_title_count = sum(1 for p in projects if p.get("title") == title)

    with allure.step(
            f"Найдено проектов с названием '{title}': {same_title_count}"):
        # Удаляем дубль, если он всё же создался
        if project_id_2:
            api.delete_project(project_id_2)

    with allure.step(
            "Проверка: должен существовать"
            "только один проект с таким названием"):
        assert same_title_count == 1, (
            f"Найдено {same_title_count} проектов с названием '{title}', "
            f"а должен быть только 1. Это баг API: создаются дубликаты."
        )


@allure.feature("Проекты")
@allure.story("Создание проекта с некорректным user_id: негативный сценарий")
@pytest.mark.negative
@pytest.mark.creation
def test_create_new_project_negative_user_id() -> None:
    """
    Проверяет обработку ошибки при создании проекта с некорректным user_id.
    Ожидается статус 400 и корректная структура сообщения об ошибке.

    Returns:
        None
    """
    title = os.getenv("TITLE")
    user_id = os.getenv("F_USER")
    s_code = int(os.getenv("STATUS_CODE"))
    wording = os.getenv("MESSAGE_1")
    note = f"{wording} {user_id}"
    misstep = os.getenv("ERROR_1")

    with allure.step("Отправка запроса с некорректным user_id"):
        status, resp = api.create_new_project(title, user_id)

    with allure.step("Проверка статус-кода"):
        assert status == 400, f"Ожидался статус 400, но получен {status}"

    with allure.step("Проверка структуры ответа об ошибке"):
        assert "statusCode" in resp, "Отсутствует поле statusCode"
        assert "message" in resp, "Отсутствует поле message"
        assert "error" in resp, "Отсутствует поле error"

        status_code = resp["statusCode"]
        message = resp["message"]
        error = resp["error"]

    with allure.step("Проверка значений полей ошибки"):
        assert status_code == s_code, (
            f"Ожидался {s_code}, но получен {status_code}")
        assert message == note, f"Ожидался '{note}', но получен '{message}'"
        assert error == misstep, f"Ожидался '{misstep}', но получен '{error}'"


@allure.feature("Проекты")
@allure.story("Переименование проекта: позитивный сценарий")
@pytest.mark.positive
@pytest.mark.rename
def test_rename_project(project: Dict[str, Any]) -> None:
    """
    Проверяет успешное переименование проекта: статус 200, ID не меняется,
    данные корректны. В конце удаляет переименованный проект.

    Args:
        project (Dict[str, Any]): данные исходного проекта из фикстуры.
    Returns:
        None
    """
    with allure.step("Валидация ID проекта из фикстуры"):
        assert "id" in project, "В ответе фикстуры отсутствует поле 'id'"
        project_id = project["id"]
        assert project_id is not None, "Поле 'id' равно None"
        assert isinstance(project_id, str), (
            f"Поле 'id' должно быть строкой, а получено: {type(project_id)}")
        assert len(project_id) > 0, "Поле 'id' пустое"

    key = os.getenv("API_KEY")
    new_title = os.getenv("NEW_TITLE")

    with allure.step(
            f"Отправка запроса на переименование:"
            f"id={project_id}, new_title={new_title}"):
        status, resp = api.update_project(project_id, new_title, key)

    with allure.step("Проверка статус-кода и структуры ответа"):
        assert status == 200, f"Ожидался статус 200, но получен {status}"
        assert "id" in resp, "В ответе отсутствует поле 'id'"

    id_project = resp["id"]

    with allure.step("Валидация ID в ответе на переименование"):
        assert id_project is not None, "Поле 'id' равно None"
        assert isinstance(id_project, str), (
            f"Поле 'id' должно быть строкой, а получено: {type(id_project)}")
        assert len(id_project) > 0, "Поле 'id' пустое"
        assert project_id == id_project, (
            f"Изменялся {project_id}, но в ответе пришёл {id_project}")

    with allure.step("Удаление переименованного проекта"):
        status_code, response = api.delete_project(id_project)

    with allure.step("Проверка ответа на удаление"):
        assert status_code == 200, (
            f"Ожидался статус 200, но получен {status_code}")

    delete_id = response["id"]
    with allure.step("Проверка совпадения ID при удалении"):
        assert delete_id == id_project, (
            f"Удалялся {id_project}, но в ответе пришёл {delete_id}")


@allure.feature("Проекты")
@allure.story(
    "Переименование проекта с неверным API‑ключом: негативный сценарий")
@pytest.mark.negative
@pytest.mark.rename
def test_rename_project_negative_id_key(project: Dict[str, Any]) -> None:
    """
    Проверяет обработку ошибки при переименовании
    проекта с некорректным API‑ключом.
    Ожидается статус 401 и корректная структура сообщения об ошибке.

    Args:
        project (Dict[str, Any]):
        данные проекта из фикстуры (используется только ID).
    Returns:
        None
    """
    with allure.step("Валидация ID проекта из фикстуры"):
        assert "id" in project, "В ответе фикстуры отсутствует поле 'id'"
        project_id = project["id"]
        assert project_id is not None, "Поле 'id' равно None"
        assert isinstance(project_id, str), (
            f"Поле 'id' должно быть строкой, а получено: {type(project_id)}")
        assert len(project_id) > 0, "Поле 'id' пустое"

    new_title = os.getenv("NEW_TITLE")
    fake_api_key = os.getenv("F_KEY")
    s_code = int(os.getenv("STATUS_CODE_1"))
    note = os.getenv("ERROR")
    misstep = os.getenv("ERROR")

    with allure.step(
            f"Отправка запроса с неверным API‑ключом:"
            f"id={project_id}, key=FAKE"):
        status, resp = api.update_project(project_id, new_title, fake_api_key)

    with allure.step("Проверка статус-кода"):
        assert status == 401, f"Ожидался статус 401, но получен {status}"

    with allure.step("Проверка структуры ответа об ошибке"):
        assert "statusCode" in resp, "Отсутствует поле statusCode"
        assert "message" in resp, "Отсутствует поле message"
        assert "error" in resp, "Отсутствует поле error"

        status_code = resp["statusCode"]
        message = resp["message"]
        error = resp["error"]

    with allure.step("Проверка значений полей ошибки"):
        assert status_code == s_code, (
            f"Ожидался {s_code}, но получен {status_code}")
        assert message == note, f"Ожидался '{note}', но получен '{message}'"
        assert error == misstep, f"Ожидался '{misstep}', но получен '{error}'"


@allure.feature("Проекты")
@allure.story("Получение проекта по ID: позитивный сценарий")
@pytest.mark.positive
@pytest.mark.get_project
def test_get_project_on_id(project: Dict[str, Any]) -> None:
    """
    Проверяет получение проекта по его ID:
    статус 200, корректность полей title и id,
    совпадение ID с исходным, соответствие title ожидаемому.
    В конце удаляет проект.

    Args:
        project (Dict[str, Any]): данные исходного проекта из фикстуры.
    Returns:
        None
    """
    with allure.step("Валидация ID проекта из фикстуры"):
        assert "id" in project, "В ответе фикстуры отсутствует поле 'id'"
        project_id = project["id"]
        assert project_id is not None, "Поле 'id' равно None"
        assert isinstance(project_id, str), (
            f"Поле 'id' должно быть строкой, а получено: {type(project_id)}")
        assert len(project_id) > 0, "Поле 'id' пустое"

    with allure.step(
            f"Отправка запроса на получение проекта по ID: {project_id}"):
        status, resp = api.get_project_on_id(project_id)

    with allure.step("Проверка статус-кода и наличия ключевых полей"):
        assert status == 200, f"Ожидался статус 200, но получен {status}"
        assert "title" in resp, "У проекта нет поля title"
        assert "id" in resp, "У проекта нет поля id"

    title = resp["title"]
    id_project = resp["id"]

    with allure.step("Проверка значений полей"):
        assert title == os.getenv("TITLE"), (
            f"Ожидается title={os.getenv('TITLE')}, но получен {title}")
        assert id_project == project_id, (
            f"Запрашивался {project_id}, но в ответе пришёл {id_project}")

    with allure.step("Удаление проекта после проверки"):
        status_code, response = api.delete_project(id_project)

    with allure.step("Проверка ответа на удаление"):
        assert status_code == 200, (
            f"Ожидался статус 200, но получен {status_code}")

    delete_id = response["id"]
    with allure.step("Проверка совпадения ID при удалении"):
        assert delete_id == id_project, (
            f"Удалялся {id_project}, но в ответе пришёл {delete_id}")


@allure.feature("Проекты")
@allure.story("Удаление проекта по ID: базовый сценарий")
@pytest.mark.positive
@pytest.mark.deletion
def test_delete_project_id(project: Dict[str, Any]) -> None:
    """
    Проверяет успешное удаление проекта по его ID:
    статус 200 и совпадение ID в ответе.
    Проект берётся из фикстуры, удаление происходит в самом тесте.

    Args:
        project (Dict[str, Any]):
        данные проекта из фикстуры (используется только ID).
    Returns:
        None
    """
    with allure.step("Извлечение ID проекта из фикстуры"):
        project_id = project["id"]
        assert project_id is not None, "Поле 'id' равно None"
        assert isinstance(project_id, str), (
            f"Поле 'id' должно быть строкой, а получено: {type(project_id)}")
        assert len(project_id) > 0, "Поле 'id' пустое"

    with allure.step(f"Отправка запроса на удаление проекта: {project_id}"):
        status_code, response = api.delete_project(project_id)

    with allure.step("Проверка статуса и совпадения ID"):
        assert status_code == 200, (
            f"Ожидался статус 200, но получен {status_code}")
        delete_id = response["id"]
        assert delete_id == project_id, (
            f"Удалялся {project_id}, но в ответе пришёл {delete_id}")


@allure.feature("Проекты")
@allure.story("Удаление несуществующего проекта: негативный сценарий")
@pytest.mark.negative
@pytest.mark.deletion
def test_delete_on_project_id_negative() -> None:
    """
    Проверяет обработку попытки удаления несуществующего проекта.
    Ожидается статус 404 и корректная структура сообщения об ошибке.

    Returns:
        None
    """
    project_id = os.getenv("F_ID_PROJECT")
    s_code = int(os.getenv("STATUS_CODE_2"))
    note = os.getenv("MESSAGE_2")
    misstep = os.getenv("ERROR_2")

    with allure.step(
            f"Отправка запроса на удаление"
            f"несуществующего проекта: {project_id}"):
        status, resp = api.delete_project(project_id)

    with allure.step("Проверка статус-кода"):
        assert status == 404, f"Ожидался статус 404, но получен {status}"

    with allure.step("Проверка структуры ответа об ошибке"):
        assert "statusCode" in resp, "Отсутствует поле statusCode"
        assert "message" in resp, "Отсутствует поле message"
        assert "error" in resp, "Отсутствует поле error"

        status_code = resp["statusCode"]
        message = resp["message"]
        error = resp["error"]

    with allure.step("Проверка значений полей ошибки"):
        assert status_code == s_code, (
            f"Ожидался {s_code}, но получен {status_code}")
        assert message == note, f"Ожидался '{note}', но получен '{message}'"
        assert error == misstep, f"Ожидался '{misstep}', но получен '{error}'"


@allure.feature("Проекты")
@allure.story("Получение списка всех проектов: позитивный сценарий")
@pytest.mark.positive
@pytest.mark.get_projects
def test_get_all_projects() -> None:
    """
    Проверяет получение списка всех проектов:
    статус 200 и корректность структуры ответа.
    Не удаляет проекты — только валидирует формат.

    Returns:
        None
    """
    with allure.step("Отправка запроса на получение списка всех проектов"):
        status_code, ress = api.get_all_projects()

    with allure.step("Проверка статус-кода и структуры ответа"):
        assert status_code == 200, (
            f"Ожидался статус 200, но получен {status_code}")
        assert "content" in ress, "Отсутствует поле content"
        assert isinstance(
            ress["content"], list), "Поле content должно быть списком"
