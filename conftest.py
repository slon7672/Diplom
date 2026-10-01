import os
import random
import string
import time
import allure
import pytest
from datetime import datetime
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver


load_dotenv()


@pytest.fixture(scope="session")
def chrome():
    options = Options()
    # options.add_argument("--headless")  # можно включить для CI
    options.add_argument("--incognito")  # в режиме инкогнито
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    driver.delete_all_cookies()

    yield driver

    driver.quit()


@pytest.fixture
def unique_project_prefix():
    """
    Генерирует уникальный префикс проекта: test + случайные буквы/цифры + временная метка
    """
    chars = string.ascii_lowercase + string.digits
    random_part = ''.join(random.choices(chars, k=5))
    timestamp = str(int(time.time()))[-4:]  # последние 4 цифры времени
    return f"test{random_part}{timestamp}"


@pytest.fixture
def take_screenshot(chrome: WebDriver):
    """
    Создает папку скриншотов и записывает скрин при вызове (опционально)
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
