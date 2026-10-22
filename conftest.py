import os
import random
import string
import allure
import pytest
from datetime import datetime
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from Pages.API_YGP import ProjectYouGile
from Pages.WebPageObject import UiPage


load_dotenv()


@pytest.fixture(scope="function")
def chrome():
    """
    Создаёт браузер.
    """
    options = Options()
    # options.add_argument("--headless")  # можно включить для CI
    options.add_argument("--incognito")  # в режиме инкогнито
    options.add_experimental_option(
        "excludeSwitches",
        ["enable-automation"])
    options.add_experimental_option(
        'useAutomationExtension',
        False)

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    driver.delete_all_cookies()

    yield driver

    driver.quit()


@pytest.fixture(scope="function")
def chrome_aut(chrome):
    """
    Принимает браузер,
    авторизуется и отдаёт готовый объект в тест.
    """
    login: str = os.getenv("LOG")
    password: str = os.getenv("PASS")
    base_url: str = os.getenv("BASE_URL_UI")
    sign_in_link: str = os.getenv("SIGN_IN_LINK_XPATH")
    e_mail_input: str = os.getenv("EMAIL_XPATH")
    pass_input: str = os.getenv("PASS_XPATH")
    login_btn: str = os.getenv("LOGIN_BTN_XPATH")
    side_bar: str = os.getenv("SIDE_BAR_XPATH")

    page = UiPage(chrome, base_url)
    page.navigate_to_base_url()
    page.click_element(sign_in_link)
    page.send_keys(e_mail_input, login)
    page.send_keys(pass_input, password)
    page.click_element(login_btn)

    assert page.is_element_present(side_bar), \
        "Сайд-бар не найден — авторизация не прошла"

    yield page


@pytest.fixture
def unique_project_prefix():
    """
    Генерирует уникальный префикс проекта:
    случайные цифры
    """
    return ''.join(random.sample(string.digits, 3))


@pytest.fixture
def take_screenshot(chrome: WebDriver):
    """
    Фикстура-помощник для скриншотов.
    Создает папку для скриншотов,
    сохраняет скрин и прикрепляет к отчёту.
    """
    def _make_screenshot(name: str = "screenshot"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        screenshot_dir = os.path.join(base_dir, "screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = os.path.join(screenshot_dir, filename)

        chrome.save_screenshot(filepath)

        allure.attach.file(
            filepath,
            name=f"Screenshot: {name}",
            attachment_type=allure.attachment_type.PNG,
        )

    yield _make_screenshot


@pytest.fixture
def created_project(chrome_aut,
                    unique_project_prefix):
    """
    Принимает авторизованную страницу,
    создает и отдает проект.
    :param chrome_aut:
    :param unique_project_prefix:
    :return: page, project_info
    """
    prefix = unique_project_prefix
    base_name = os.getenv("NAME_PROJECT")
    project_name = f"{prefix}_{base_name}"
    my_company = os.getenv("MY_COMPANY_XPATH")
    company_label = os.getenv("NAME_PAGE_MY_COMPANY_XPATH")
    btn_add_project = os.getenv("ADD_BTN_P_XPATH")
    input_name = os.getenv("IN_NAME_P_XPATH")
    btn_menu_projects = os.getenv("ADD_PROJECT_BTN_XPATH")
    btn_param_project = os.getenv("PROJECT_TASK_XPATH")

    # Навигация на страницу проектов
    page = chrome_aut
    assert page.is_element_present(my_company), \
        "Не найдена кнопка 'Моя компания'"
    assert page.is_element_present(company_label), \
        "Не загрузилась страница компании"

    # Открытие формы создания
    page.click_element(btn_menu_projects)
    page.click_element(btn_param_project)

    # Заполнение и отправка
    page.send_keys(input_name, project_name)
    page.click_element(btn_add_project)
    project_info = {
        "name": project_name,
        "prefix": prefix
    }

    yield page, project_info

    # Удаление через API
    api = ProjectYouGile()
    status, body = api.get_all_projects()
    projects = body.get("content", [])

    project_id = None
    for p in projects:
        if p.get("title") == project_name:
            project_id = p.get("id")
            break

    if project_id:
        api.delete_project(project_id)
