import os
from typing import Any, Tuple, Optional, Dict
import allure
import pytest
from dotenv import load_dotenv
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from Pages.API_YGP import ProjectYouGile
from Pages.WebPageObject import UiPage
from selenium.webdriver.common.action_chains import ActionChains

load_dotenv()


@allure.feature("Авторизация")
@allure.story("Успешная авторизация пользователя через UI")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.ui
@pytest.mark.aut
@pytest.mark.positive
def test_aut(chrome):
    """
    Проверяет вход в систему с валидными учётными данными
    и наличие сайд‑бара как индикатора успешной авторизации.

    Входные данные (из .env):
        - LOGIN, PASSWORD: учётные данные пользователя.
        - BASE_URL_UI: адрес приложения.
        - Локаторы (XPath): SIGN_IN_LINK_XPATH, EMAIL_XPATH,
          PASS_XPATH, LOGIN_BTN_XPATH, SIDE_BAR_XPATH.

    Зависимости:
        - chrome: экземпляр браузера (фикстура pytest).
        - UiPage: Page Object для взаимодействия со страницей.

    Ожидаемый результат:
        - Пользователь авторизован.
        - На странице отображается сайд‑бар.
        - Тест завершается без ошибок, выводится сообщение
          «Авторизация успешно пройдена».

    Returns:
        None
    """
    # Тестовые данные
    login: str = os.getenv("LOG")
    password: str = os.getenv("PASS")
    base_url: str = os.getenv("BASE_URL_UI")

    page = UiPage(chrome, base_url)

    # Блок настройки селекторов для взаимодействия
    sign_in_link: str = os.getenv("SIGN_IN_LINK_XPATH")
    e_mail_input: str = os.getenv("EMAIL_XPATH")
    pass_input: str = os.getenv("PASS_XPATH")
    login_btn: str = os.getenv("LOGIN_BTN_XPATH")
    side_bar: str = os.getenv("SIDE_BAR_XPATH")

    with allure.step("Переход на главную страницу"):
        page.navigate_to_base_url()

    with allure.step("Клик по ссылке «Войти»"):
        page.click_element(sign_in_link)

    with allure.step("Ввод логина и пароля"):
        page.send_keys(e_mail_input, login)
        page.send_keys(pass_input, password)

    with allure.step("Нажатие кнопки входа"):
        page.click_element(login_btn)

    with allure.step("Проверка успешности авторизации (наличие сайд‑бара)"):
        assert page.is_element_present(side_bar), \
            "Сайд‑бар не найден — авторизация не прошла"


@allure.feature("Авторизация")
@allure.story("Неудачная авторизация: неверные логин и пароль")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.ui
@pytest.mark.aut
@pytest.mark.negative
def test_aut_negative(chrome: WebDriver, take_screenshot: Any) -> None:
    """
    Проверяет поведение системы при попытке авторизации
    с некорректными учётными данными.

    Входные данные:
        - login = "login", password = "password" — заведомо неверные
          учётные данные для проверки негативной ветки.
        - BASE_URL_UI: адрес приложения (из .env).
        - Локаторы (XPath): SIGN_IN_LINK_XPATH, EMAIL_XPATH,
          PASS_XPATH, LOGIN_BTN_XPATH — для взаимодействия с формой входа.
        - LOGIN_ERR_XPATH: локатор элемента с сообщением об ошибке
          (критерий успеха негативного сценария).

    Зависимости:
        - chrome: экземпляр браузера (фикстура pytest).
        - take_screenshot: фикстура для сохранения скриншота при ошибке.
        - UiPage: Page Object для взаимодействия со страницей.

    Ожидаемый результат:
        - Система не допускает вход с неверными данными.
        - На странице отображается сообщение об ошибке авторизации
          (элемент по локатору LOGIN_ERR_XPATH).
        - Тест завершается успешно (проходит ассерт), делается скриншот
          с подписью «Ошибка авторизации».

    Returns:
        None
    """
    base_url: str = os.getenv("BASE_URL_UI")

    # Тестовые данные
    login: str = "login"
    password: str = "password"

    # Блок настройки селекторов для взаимодействия
    sign_in_link: str = os.getenv("SIGN_IN_LINK_XPATH")
    e_mail_input: str = os.getenv("EMAIL_XPATH")
    pass_input: str = os.getenv("PASS_XPATH")
    login_btn: str = os.getenv("LOGIN_BTN_XPATH")
    login_err: str = os.getenv("LOGIN_ERR_XPATH")

    page = UiPage(chrome, base_url)

    with allure.step("Переход на главную страницу"):
        page.navigate_to_base_url()

    with allure.step("Клик по ссылке «Войти»"):
        page.click_element(sign_in_link)

    with allure.step("Ввод некорректных логина и пароля"):
        page.send_keys(e_mail_input, login)
        page.send_keys(pass_input, password)

    with allure.step("Нажатие кнопки входа"):
        page.click_element(login_btn)

    with allure.step("Проверка появления сообщения об ошибке авторизации"):
        assert page.find_element_by_xpath(login_err), \
            "Сообщение об ошибке не найдено — авторизация прошла успешно, " \
            "хотя должны были быть неверные данные"

    with allure.step("Сохранение скриншота ошибки"):
        take_screenshot("Ошибка авторизации")


@allure.feature("Смок-тесты UI")
@allure.story("Проверка навигации в сайд-баре: опция «Моя компания»")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ui
@pytest.mark.smoke
@pytest.mark.company
@pytest.mark.positive
def test_company_present(
        chrome_aut: WebDriver,
        take_screenshot: Any) -> None:
    """
    Проверяет наличие и открытие страницы «Моя компания»
    через пункт в сайд-баре после авторизации.

    Входные данные:
        - SIDE_BAR_XPATH: локатор сайд‑бара
          (подтверждение, что пользователь авторизован).
        - MY_COMPANY_XPATH: локатор пункта «Моя компания» в меню.
        - NAME_PAGE_MY_COMPANY_XPATH: заголовок/элемент, подтверждающий
          открытие страницы «Моя компания».

    Зависимости:
        - chrome_aut: авторизованный экземпляр браузера (фикстура).
        - take_screenshot: фикстура для сохранения скриншота.

    Ожидаемый результат:
        - Элемент сайд‑бара присутствует.
        - Пункт «Моя компания» виден в меню.
        - После клика открывается страница «Моя компания»,
          подтверждаемый элементом NAME_PAGE_MY_COMPANY_XPATH.
        - Делается скриншот «company_page_present».

    Returns:
        None
    """
    page = chrome_aut

    side_bar: str = os.getenv("SIDE_BAR_XPATH")
    my_company: str = os.getenv("MY_COMPANY_XPATH")
    company_label: str = os.getenv("NAME_PAGE_MY_COMPANY_XPATH")

    with allure.step("Проверка наличия сайд‑бара и пункта «Моя компания»"):
        assert page.is_element_present(side_bar), \
            "Сайд‑бар не найден — пользователь не авторизован"
        assert page.is_element_present(my_company), \
            "Пункт «Моя компания» отсутствует в меню"

    with allure.step("Клик по пункту «Моя компания»"):
        page.click_element(my_company)

    with allure.step("Подтверждение открытия страницы «Моя компания»"):
        assert page.is_element_present(company_label), \
            "Страница «Моя компания» не открылась"

    with allure.step("Сохранение скриншота"):
        take_screenshot("Страница компании")


@allure.feature("Смок-тесты UI")
@allure.story("Проверка навигации в сайд-баре: опция «Мессенджер»")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ui
@pytest.mark.smoke
@pytest.mark.messenger
@pytest.mark.positive
def test_messenger_present(
        chrome_aut: WebDriver,
        take_screenshot: Any) -> None:
    """
    Проверяет наличие и открытие страницы «Мессенджер»
    через пункт в сайд-баре.

    Входные данные:
        - MESSENGER_XPATH: локатор пункта «Мессенджер» в меню.
        - NAME_PAGE_MESSENG_XPATH: элемент, подтверждающий
          открытие страницы «Мессенджер».

    Зависимости:
        - chrome_aut: авторизованный экземпляр браузера (фикстура).
        - take_screenshot: фикстура для сохранения скриншота.

    Ожидаемый результат:
        - Пункт «Мессенджер» присутствует в меню.
        - После клика открывается страница «Мессенджер»,
          подтверждаемая элементом NAME_PAGE_MESSENG_XPATH.
        - Делается скриншот «messenger_page_present».

    Returns:
        None
    """
    page = chrome_aut

    messenger: str = os.getenv("MESSENGER_XPATH")
    messenger_label: str = os.getenv("NAME_PAGE_MESSENG_XPATH")

    with allure.step("Проверка наличия пункта «Мессенджер»"):
        assert page.is_element_present(messenger), \
            "Пункт «Мессенджер» отсутствует в меню"

    with allure.step("Клик по пункту «Мессенджер»"):
        page.click_element(messenger)

    with allure.step("Подтверждение открытия страницы «Мессенджер»"):
        assert page.is_element_present(messenger_label), \
            "Страница «Мессенджер» не открылась"

    with allure.step("Сохранение скриншота"):
        take_screenshot("messenger_page_present")


@allure.feature("Смок-тесты UI")
@allure.story("Проверка навигации в сайд-баре: опция «Лента событий»")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ui
@pytest.mark.smoke
@pytest.mark.event
@pytest.mark.positive
def test_event_present(chrome_aut: WebDriver, take_screenshot: Any) -> None:
    """
    Проверяет наличие и открытие страницы «Лента событий»
    через пункт в сайд-баре.

    Входные данные:
        - EVENT_FEED_XPATH: локатор пункта «Лента событий» в меню.
        - NAME_PAGE_EVENT_XPATH: элемент, подтверждающий
          открытие страницы «Лента событий».

    Зависимости:
        - chrome_aut: авторизованный экземпляр браузера (фикстура).
        - take_screenshot: фикстура для сохранения скриншота.

    Ожидаемый результат:
        - Пункт «Лента событий» присутствует в меню.
        - После клика открывается страница «Лента событий»,
          подтверждаемая элементом NAME_PAGE_EVENT_XPATH.
        - Делается скриншот «event_page_present».

    Returns:
        None
    """
    page = chrome_aut

    event: str = os.getenv("EVENT_FEED_XPATH")
    event_label: str = os.getenv("NAME_PAGE_EVENT_XPATH")

    with (allure.step("Проверка наличия пункта «Лента событий»")):
        assert page.is_element_present(event), \
            "Пункт «Лента событий» отсутствует в меню"

    with allure.step("Клик по пункту «Лента событий»"):
        page.click_element(event)

    with ((allure.step("Подтверждение открытия страницы «Лента событий»"))):
        assert page.is_element_present(event_label), \
                "Страница «Лента событий» не открылась"

    with allure.step("Сохранение скриншота"):
        take_screenshot("event_page_present")


@allure.feature("Проекты")
@allure.story("Создание проекта через UI и проверка отображения в сайд‑баре")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ui
@pytest.mark.projects
@pytest.mark.positive
def test_created_project(
        chrome_aut: WebDriver,
        unique_project_prefix: Any,
        take_screenshot: Any) -> None:
    """
    Проверяет создание проекта через UI: открытие формы, ввод имени,
    активацию кнопки «Добавить проект» и отображение проекта в сайд‑баре.
    В конце удаляет созданный проект через API для очистки тестовых данных.

    Входные данные:
        - unique_project_prefix: префикс проекта (генерируется фикстурой,
          гарантирует уникальность).
        - NAME_PROJECT: базовый шаблон имени проекта (из .env).
        - Локаторы: ADD_BTN_P_XPATH, IN_NAME_P_XPATH, ADD_PROJECT_BTN_XPATH,
          PROJECT_TASK_XPATH — элементы формы создания проекта.

    Зависимости:
        - chrome_aut: авторизованный экземпляр браузера (фикстура).
        - unique_project_prefix: фикстура для генерации уникального префикса.
        - take_screenshot: фикстура для сохранения скриншота.
        - ProjectYouGile: класс для API‑удаления проекта.

    Ожидаемый результат:
        - Кнопка «Добавить проект» неактивна до ввода имени.
        - После ввода имени кнопка становится активной.
        - Проект отображается в сайд‑баре (поиск по префиксу в data-testid).
        - Созданный проект удаляется через API.
        - Делается скриншот «Созданый проект».

    Returns:
        None
    """
    prefix = unique_project_prefix
    base_name: str = os.getenv("NAME_PROJECT")
    project_name = f"{prefix}_{base_name}"

    btn_add_project: str = os.getenv("ADD_BTN_P_XPATH")
    input_name: str = os.getenv("IN_NAME_P_XPATH")
    btn_menu_projects: str = os.getenv("ADD_PROJECT_BTN_XPATH")
    btn_param_project: str = os.getenv("PROJECT_TASK_XPATH")

    sidebar_project_created = (
        f'//div[@data-testid="left-sidebar"]'
        f'//div[@data-testid="projects-list"]'
        f'//div[@data-testid="project-item"]'
        f'[.//div[contains(@class, "truncate") '
        f'and starts-with(normalize-space(text()), '
        f'"{unique_project_prefix}")]]'
    )

    page = chrome_aut

    with allure.step("Открытие формы создания проекта"):
        page.click_element(btn_menu_projects)
        page.click_element(btn_param_project)

    with allure.step(
            "Проверка активности кнопки «Добавить проект»"):
        assert not page.is_button_enabled(btn_add_project), \
            "Кнопка 'Добавить проект' активна до ввода имени"

    with allure.step("Ввод имени проекта"):
        page.send_keys(input_name, project_name)

    with allure.step(
            "Проверка активации кнопки «Добавить проект» после ввода имени"):
        assert page.is_button_enabled(btn_add_project), \
            "Кнопка 'Добавить проект' не стала активной после ввода имени"
        page.click_element(btn_add_project)

    with allure.step("Проверка отображения проекта в сайд‑баре"):
        if not page.is_element_present(sidebar_project_created, by=By.XPATH):
            take_screenshot("error_project_not_found_in_sidebar")
            assert False, (
                f"Проект с префиксом '{unique_project_prefix}' "
                f"не отобразился в сайд‑баре за отведённое время."
            )
        else:
            print(f"Проект '{project_name}' успешно найден в сайд‑баре.")

    with allure.step("Сохранение скриншота успешного создания"):
        take_screenshot("Созданный проект")

    with allure.step("Очистка: удаление созданного проекта через API"):
        api: ProjectYouGile = ProjectYouGile()
        status: int
        body: dict
        status, body = api.get_all_projects()
        projects: list[dict] = body.get("content", [])

        project_id: Optional[str] = None
        for p in projects:
            if p.get("title") == project_name:
                project_id = p.get("id")
                break

        if project_id:
            api.delete_project(project_id)
            print(f"Проект '{project_name}' удалён через API.")
        else:
            print(
                f"Проект '{project_name}' не найден в списке — "
                f"возможно, уже удалён.")


@allure.feature("Проекты")
@allure.story(
    "Попытка создания проекта с недопустимым именем: "
    "кнопка не активируется")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ui
@pytest.mark.projects
@pytest.mark.negative
def test_created_project_negative(
        chrome_aut: WebDriver,
        take_screenshot: Any) -> None:
    """
    Проверяет поведение UI при попытке создания проекта с именем,
    которое не позволяет активировать кнопку «Добавить проект».
    Сценарий подтверждает, что система не даёт создать проект
    с некорректным/неполным именем.

    Входные данные:
        - NAME_PROJECT_NEGATIVE:
          шаблон имени для негативного сценария (из .env),
          который не приводит к активации кнопки.
        - Локаторы: ADD_BTN_P_XPATH, IN_NAME_P_XPATH, ADD_PROJECT_BTN_XPATH,
          PROJECT_TASK_XPATH — элементы формы создания проекта.

    Зависимости:
        - chrome_aut: авторизованный экземпляр браузера (фикстура).
        - take_screenshot: фикстура для сохранения скриншота.

    Ожидаемый результат:
        - Кнопка «Добавить проект» остаётся неактивной даже после ввода имени.
        - Проект не создаётся (нет необходимости в удалении).
        - Делается скриншот «error_project_creation_negative».

    Returns:
        None
    """
    base_name: str = os.getenv("NAME_PROJECT_NEGATIVE")
    project_name = f"{base_name}"

    btn_add_project: str = os.getenv("ADD_BTN_P_XPATH")
    input_name: str = os.getenv("IN_NAME_P_XPATH")
    btn_menu_projects: str = os.getenv("ADD_PROJECT_BTN_XPATH")
    btn_param_project: str = os.getenv("PROJECT_TASK_XPATH")

    page = chrome_aut

    with allure.step("Открытие формы создания проекта"):
        page.click_element(btn_menu_projects)
        page.click_element(btn_param_project)

    with allure.step(
            "Проверка, что кнопка «Добавить проект» изначально неактивна"):
        assert not page.is_button_enabled(btn_add_project), \
            "Кнопка 'Добавить проект' активна до ввода имени"

    with allure.step("Ввод недопустимого имени проекта"):
        page.send_keys(input_name, project_name)

    with allure.step("Подтверждение, что кнопка остаётся неактивной"):
        assert not page.is_button_enabled(btn_add_project), \
            "Кнопка 'Добавить проект' стала активной, хотя имя недопустимо"

    with allure.step("Сохранение скриншота негативного сценария"):
        take_screenshot("error_project_creation_negative")


@allure.feature("Доски")
@allure.story("Создание доски с валидным названием в проекте")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ui
@pytest.mark.boards
@pytest.mark.positive
def test_add_board_in_project(
        created_project: Tuple[UiPage, Dict[str, Any]],
        take_screenshot: Any) -> None:
    """
    Проверяет создание доски в проекте: открытие меню, выбор типа,
    ввод названия и подтверждение нажатием Enter.

    Входные данные:
        - NAME_BOARD: шаблон имени доски (из .env).
        - Локаторы: BTN_ADD_BOARD_XPATH, BTN_MENU_ADD_BOARD_XPATH —
          элементы для вызова формы создания доски.

    Зависимости:
        - created_project: фикстура, возвращающая (page, project_info)
          для уже созданного проекта.
        - take_screenshot: фикстура для сохранения скриншота.

    Ожидаемый результат:
        - После ввода имени и нажатия Enter
          доска отображается в списке вкладок.
        - Элемент с названием доски присутствует на странице.
        - Делается скриншот «Созданная доска».

    Returns:
        None
    """
    name_board: str = os.getenv("NAME_BOARD")

    btn_add_board: str = os.getenv("BTN_ADD_BOARD_XPATH")
    btn_menu_add_board: str = os.getenv("BTN_MENU_ADD_BOARD_XPATH")

    page, project_info = created_project

    with allure.step("Клик по кнопке «+» для добавления доски"):
        page.click_element(btn_add_board)

    with allure.step("Выбор пункта «Доска с задачами» в выпадающем меню"):
        page.click_element(btn_menu_add_board)

    with allure.step(
            f"Ввод названия доски: {name_board} и подтверждение Enter"):
        ActionChains(page.browser).send_keys(name_board).perform()
        page.press_key("ENTER")

    with allure.step("Сохранение скриншота созданной доски"):
        take_screenshot("Созданная доска")

    board_locator = f"//div[contains(text(), '{name_board}')]"

    with allure.step("Проверка отображения созданной доски"):
        assert page.is_element_present(board_locator), \
            f"Доска с названием '{name_board}' не создана"


@allure.feature("Доски")
@allure.story("Попытка создания доски с невалидным названием (только пробелы)")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ui
@pytest.mark.boards
@pytest.mark.negative
def test_add_board_in_project_negative(
        created_project: Tuple[UiPage, Dict[str, Any]],
        take_screenshot: Any) -> None:
    """
    Проверяет поведение системы при попытке создать доску
    с невалидным именем (только пробелы).

    Сценарий основан на подсчёте количества вкладок до и после попытки:
    если доска не создаётся — количество вкладок не меняется.

    Входные данные:
        - name_board = "   ": невалидное имя (пробелы), которое не должно
          привести к созданию доски.
        - Локаторы: BTN_ADD_BOARD_XPATH, BTN_MENU_ADD_BOARD_XPATH —
          элементы меню создания.
        - BOARD_TABS_CONTAINER_XPATH: локатор контейнера с вкладками досок,
          по которому считаем количество досок.

    Зависимости:
        - created_project: фикстура, возвращающая (page, project_info)
          для существующего проекта.
        - take_screenshot: фикстура для сохранения скриншота.

    Ожидаемый результат:
        - При вводе только пробелов и нажатии Enter доска не создаётся.
        - Количество вкладок до и после попытки остаётся одинаковым.
        - Делается скриншот «Попытка создания доски с невалидным именем».

    Returns:
        None
    """
    name_board: str = "   "

    btn_add_board: str = os.getenv("BTN_ADD_BOARD_XPATH")
    btn_menu_add_board: str = os.getenv("BTN_MENU_ADD_BOARD_XPATH")
    board_tabs_container: str = os.getenv("BOARD_TABS_CONTAINER_XPATH")

    page, project_info = created_project

    with allure.step(
            "Подсчёт количества вкладок досок ДО попытки создания"):
        tabs_before = page.find_elements_by_xpath(board_tabs_container)
        count_before = len(tabs_before)

    with allure.step(
            "Клик по кнопке «+» и выбор «Доска с задачами»"):
        page.click_element(btn_add_board)
        page.click_element(btn_menu_add_board)

    with allure.step(
            f"Ввод невалидного имени («{name_board}») и подтверждение Enter"):
        ActionChains(page.browser).send_keys(name_board).perform()
        page.press_key("ENTER")

    with allure.step(
            "Сохранение скриншота попытки создания с невалидным именем"):
        take_screenshot("Попытка создания доски с невалидным именем")

    with allure.step("Подсчёт количества вкладок ПОСЛЕ попытки создания"):
        tabs_after = page.find_elements_by_xpath(board_tabs_container)
        count_after = len(tabs_after)

    with allure.step(
            "Проверка, "
            "что количество вкладок не изменилось (доска не создана)"):
        assert count_after == count_before, (
            f"Доска с невалидным именем '{name_board}' была создана! "
            f"Было вкладок: {count_before}, стало: {count_after}"
        )


@allure.feature("Проекты и доски")
@allure.story("Создание колонки на доске проекта")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ui
@pytest.mark.columns
@pytest.mark.positive
def test_add_column_in_board(
        created_project: Tuple[UiPage, Dict[str, Any]],
        take_screenshot: Any) -> None:
    """
    Проверяет полный сценарий: создание доски в проекте и добавление
    колонки на эту доску.

    Входные данные:
        - NAME_BOARD: шаблон имени доски (из .env).
        - NAME_COLUMN: шаблон имени колонки (из .env).
        - Локаторы: BTN_ADD_BOARD_XPATH, BTN_MENU_ADD_BOARD_XPATH —
          для создания доски; BTN_ADD_COLUMN_XPATH — для создания колонки.

    Зависимости:
        - created_project: фикстура, возвращающая (page, project_info)
          для уже созданного проекта.
        - take_screenshot: фикстура для сохранения скриншота.

    Ожидаемый результат:
        - Доска успешно создана и отображается на странице.
        - Колонка успешно создана и видна в структуре доски.
        - Элемент с названием колонки присутствует (по data-testid и тексту).
        - Делается скриншот «Созданная колонка».

    Returns:
        None
    """
    name_board: str = os.getenv("NAME_BOARD")
    name_column: str = os.getenv("NAME_COLUMN")

    btn_add_board: str = os.getenv("BTN_ADD_BOARD_XPATH")
    btn_menu_add_board: str = os.getenv("BTN_MENU_ADD_BOARD_XPATH")
    btn_add_column: str = os.getenv("BTN_ADD_COLUMN_XPATH")

    page, project_info = created_project

    with allure.step("Клик по кнопке «+» для добавления доски"):
        page.click_element(btn_add_board)

    with allure.step("Выбор пункта «Доска с задачами» в выпадающем меню"):
        page.click_element(btn_menu_add_board)

    with allure.step(
            f"Ввод названия доски: {name_board} и подтверждение Enter"):
        ActionChains(page.browser).send_keys(name_board).perform()
        page.press_key("ENTER")

    board_locator = f"//div[contains(text(), '{name_board}')]"

    with allure.step("Проверка отображения созданной доски"):
        assert page.is_element_present(board_locator), \
            f"Доска с названием '{name_board}' не создана"

    with allure.step("Клик по кнопке «+ Создать колонку»"):
        page.click_element(btn_add_column)

    with allure.step(
            f"Ввод названия колонки: {name_column} и подтверждение Enter"):
        ActionChains(page.browser).send_keys(name_column).perform()
        page.press_key("ENTER")

    with allure.step("Сохранение скриншота созданной колонки"):
        take_screenshot("Созданная колонка")

    column_locator = (
        f"//div[@data-testid='board-column' "
        f"and .//span[contains(text(), '{name_column}')]]"
    )

    with allure.step("Проверка отображения созданной колонки"):
        assert page.is_element_present(column_locator), \
            f"Колонка с названием '{name_column}' не создана"


@allure.feature("Проекты и доски")
@allure.story("Создание задачи в колонке на доске проекта")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ui
@pytest.mark.tasks
@pytest.mark.positive
def test_add_task_in_column_and_task(
        created_project: Tuple[UiPage, Dict[str, Any]],
        take_screenshot: Any) -> None:
    """
    Проверяет полный сценарий: создание доски → создание колонки →
    создание задачи в этой колонке.

    Входные данные:
        - NAME_BOARD: шаблон имени доски (из .env).
        - NAME_COLUMN: шаблон имени колонки (из .env).
        - NAME_TASK: шаблон имени задачи (из .env).
        - Локаторы: BTN_ADD_BOARD_XPATH, BTN_MENU_ADD_BOARD_XPATH —
          для создания доски; BTN_ADD_COLUMN_XPATH — для создания колонки;
          динамический локатор для кнопки «+ Добавить задачу»
          строится по имени колонки.

    Зависимости:
        - created_project: фикстура, возвращающая (page, project_info)
          для уже созданного проекта.
        - take_screenshot: фикстура для сохранения скриншота.

    Ожидаемый результат:
        - Доска успешно создана и отображается на странице.
        - Колонка успешно создана и видна в структуре доски.
        - Задача успешно создана и
          отображена в карточке (по data-testid и тексту).
        - Делается скриншот «Созданная задача».

    Returns:
        None
    """
    name_board: str = os.getenv("NAME_BOARD")
    name_column: str = os.getenv("NAME_COLUMN")
    name_task: str = os.getenv("NAME_TASK")

    btn_add_board: str = os.getenv("BTN_ADD_BOARD_XPATH")
    btn_menu_add_board: str = os.getenv("BTN_MENU_ADD_BOARD_XPATH")
    btn_add_column: str = os.getenv("BTN_ADD_COLUMN_XPATH")

    page, project_info = created_project

    with allure.step("Клик по кнопке «+» для добавления доски"):
        page.click_element(btn_add_board)

    with allure.step("Выбор пункта «Доска с задачами» в выпадающем меню"):
        page.click_element(btn_menu_add_board)

    with allure.step(
            f"Ввод названия доски: "
            f"{name_board} и подтверждение Enter"):
        ActionChains(page.browser).send_keys(name_board).perform()
        page.press_key("ENTER")

    board_locator = f"//div[contains(text(), '{name_board}')]"

    with allure.step("Проверка отображения созданной доски"):
        assert page.is_element_present(board_locator), \
            f"Доска с названием '{name_board}' не создана"

    with allure.step("Клик по кнопке «+ Создать колонку»"):
        page.click_element(btn_add_column)

    with allure.step(
            f"Ввод названия колонки: "
            f"{name_column} и подтверждение Enter"):
        ActionChains(page.browser).send_keys(name_column).perform()
        page.press_key("ENTER")

    column_locator = (
        f"//div[@data-testid='board-column' "
        f"and .//span[contains(text(), '{name_column}')]]"
    )

    with allure.step("Проверка отображения созданной колонки"):
        assert page.is_element_present(column_locator), \
            f"Колонка с названием '{name_column}' не создана"

    # Динамический локатор кнопки «+ Добавить задачу» внутри нужной колонки
    btn_add_task = (
        f"//div[@data-testid='board-column' and "
        f".//span[contains(text(), '{name_column}')]]"
        f"//div[@data-testid='link-button-new']"
    )

    with allure.step("Клик по кнопке «+ Добавить задачу» в нужной колонке"):
        page.click_element(btn_add_task)

    with allure.step(
            f"Ввод названия задачи: {name_task}, "
            f"подтверждение Enter и закрытие формы ESC"):
        ActionChains(page.browser).send_keys(name_task).perform()
        page.press_key("ENTER")
        page.press_key("ESCAPE")

    with allure.step("Сохранение скриншота созданной задачи"):
        take_screenshot("Созданная задача")

    task_locator = (
        f'//div[@data-testid="board-task-card"]'
        f'[.//div[@data-testid="board-task-title"]//span'
        f'[contains(normalize-space(text()), "{name_task}")]]'
    )

    with allure.step("Проверка отображения созданной задачи"):
        assert page.is_element_present(task_locator), \
            f"Задача с названием '{name_task}' не создана"
