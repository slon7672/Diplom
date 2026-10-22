import allure
from selenium.common.exceptions import (
    StaleElementReferenceException,
    ElementNotInteractableException,
    ElementClickInterceptedException,
    TimeoutException,
)
from typing import List

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


class UiPage:
    def __init__(
        self,
        browser,
        base_url: str,
        timeout: int = 60,
        poll_frequency: float = 0.5,
    ):
        """
        Инициализация класса.

        :param browser: Экземпляр WebDriver
        :param base_url: базовый URL для загрузки страницы
        :param timeout: время ожидания в секундах
        :param poll_frequency: частота проверки условий в секундах
        """
        self.browser = browser
        self.base_url = base_url
        self.timeout = timeout
        self.poll_frequency = poll_frequency
        self.wait = WebDriverWait(
            self.browser, self.timeout, self.poll_frequency
        )

    @allure.step("Переход на базовый URL")
    def navigate_to_base_url(self) -> None:
        """Вызов базового URL."""
        with allure.step(f"Открытие URL: {self.base_url}"):
            self.browser.get(self.base_url)

    @allure.step("Получение текущего URL страницы")
    def get_current_url(self) -> str:
        """Возвращает текущий URL страницы."""
        current_url = self.browser.current_url
        with allure.step(f"Текущий URL: {current_url}"):
            pass
        return current_url

    @allure.step("Ожидание, пока URL содержит фрагмент: {fragment}")
    def wait_url(self, fragment: str, timeout: int = None) -> str:
        """
        "Wait_for_url_contains"
        Ждёт, пока в текущем URL появится указанный фрагмент.
        Возвращает финальный URL.

        :param fragment: подстрока, которую ищем в URL (например, 'messenger')
        :param timeout: опциональный таймаут (перекрывает стандартный)
        """

        wait_obj = WebDriverWait(
            self.browser,
            timeout if timeout is not None else self.timeout,
            self.poll_frequency
        )

        with allure.step(
                f"Ожидание появления '{fragment}' в URL ("
                f"таймаут: {wait_obj._timeout} сек)..."):
            wait_obj.until(lambda d: fragment in d.current_url)

        return self.get_current_url()

    @allure.step("Поиск элемента по CSS‑селектору: {css_selector}")
    def find_element_by_css(self, css_selector: str) -> WebElement:
        return self.wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, css_selector)
            )
        )

    @allure.step("Поиск элемента по XPath‑селектору: {xpath_selector}")
    def find_element_by_xpath(self, xpath_selector: str) -> WebElement:
        return self.wait.until(
            EC.visibility_of_element_located((By.XPATH, xpath_selector))
        )

    @allure.step("Поиск всех элементов по CSS‑селектору: {css_selector}")
    def find_elements_by_css(self, css_selector: str) -> List[WebElement]:
        return self.wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, css_selector)
            )
        )

    @allure.step("Поиск всех элементов по XPath‑селектору: {xpath_selector}")
    def find_elements_by_xpath(self, xpath_selector: str) -> List[WebElement]:
        return self.wait.until(
            EC.presence_of_all_elements_located((By.XPATH, xpath_selector))
        )

    @allure.step(
        "Ввод текста '{text}' в элемент по селектору '{selector}' (тип: {by})")
    def send_keys(
        self,
        selector: str,
        text: str,
        max_attempts: int = 3,
        by: By = By.XPATH,
    ) -> WebElement:
        """
        Надёжно вводит текст в поле с повторными попытками.
        При неудаче выбрасывает исключение.
        """
        for attempt in range(1, max_attempts + 1):
            with allure.step(f"Попытка {attempt}/{max_attempts} ввода текста"):
                try:
                    with allure.step("Ожидание кликабельности элемента"):
                        element = self.wait.until(
                            EC.element_to_be_clickable((by, selector))
                        )
                    with allure.step("Прокрутка к элементу"):
                        self.browser.execute_script(
                            "arguments[0].scrollIntoView(true);", element
                        )
                    with allure.step("Очистка поля ввода"):
                        element.clear()
                    with allure.step(f"Ввод текста: '{text}'"):
                        element.send_keys(text)
                    return element
                except StaleElementReferenceException:
                    if attempt == max_attempts:
                        with allure.step(
                                "Исчерпаны все попытки — "
                                "пробрасываем StaleElementReferenceException"):
                            raise
                    with allure.step("Элемент устарел — повторяем попытку"):
                        continue

        # Сюда код не должен доходить, но для ясности:
        raise Exception(
            f"Не удалось ввести текст после {max_attempts} попыток")

    @allure.step("Клик по элементу с селектором '{selector}' (тип: {by})")
    def click_element(
        self,
        selector: str,
        max_attempts: int = 3,
        by: By = By.XPATH,
    ) -> WebElement:
        """
        Надёжно кликает по элементу.
        Сначала — JS-клик, при неудаче — попытка через ActionChains.
        Если все попытки исчерпаны — выбрасывает исключение.
        """
        for attempt in range(1, max_attempts + 1):
            with allure.step(
                    f"Попытка {attempt}/{max_attempts} клика по элементу"):
                try:
                    with allure.step(
                            "Поиск и ожидание кликабельности элемента"):
                        element = self.wait.until(
                            EC.element_to_be_clickable((by, selector))
                        )
                    with allure.step("Прокрутка к элементу (центрирование)"):
                        self.browser.execute_script(
                            "arguments[0].scrollIntoView({block: 'center'});",
                            element,
                        )
                    with allure.step("Основной клик через JavaScript"):
                        self.browser.execute_script(
                            "arguments[0].click();", element)
                    return element

                except StaleElementReferenceException:
                    if attempt == max_attempts:
                        raise
                    with allure.step("Элемент устарел — повторная попытка"):
                        continue

                except (
                        ElementNotInteractableException,
                        ElementClickInterceptedException):
                    # Пробуем альтернативный клик только один раз на попытку
                    with allure.step(
                            "Попытка альтернативного клика (ActionChains)"):
                        try:
                            short_wait = WebDriverWait(
                                self.browser, timeout=2, poll_frequency=0.1)
                            alt_element = short_wait.until(
                                EC.element_to_be_clickable((by, selector))
                            )
                            actions = ActionChains(self.browser)
                            actions.move_to_element(
                                alt_element
                            ).click().perform()
                            return alt_element
                        except (
                                StaleElementReferenceException,
                                ElementNotInteractableException):
                            with allure.step(
                                    "Альтернативный клик не сработал — "
                                    "следующая попытка"):
                                continue
                        except Exception:
                            # Если альтернативный клик дал другую ошибку —
                            # тоже идём на следующую попытку
                            with allure.step(
                                    "Ошибка при альтернативном клике — "
                                    "следующая попытка"):
                                continue

        raise Exception(
            f"Не удалось кликнуть по элементу '{selector}' "
            f"после {max_attempts} попыток")

    @allure.step("Получение текста из элемента '{selector}'")
    def get_text(self, selector: str, by: By = By.XPATH) -> str:
        element = self.wait.until(
            EC.visibility_of_element_located((by, selector))
        )
        return element.text

    @allure.step("Проверка наличия элемента: '{selector}' (тип: {by})")
    def is_element_present(self, selector: str, by: By = By.XPATH) -> bool:
        """
        Проверяет наличие элемента без выброса исключения.
        Возвращает True, если элемент найден за время ожидания, иначе False.
        """

        try:
            with allure.step(
                    f"Ожидание появления элемента по селектору: {selector}"):
                self.wait.until(
                    EC.presence_of_element_located((by, selector))
                )
            with allure.step("Элемент найден — возвращаем True"):
                return True
        except TimeoutException:
            with allure.step(
                    "Элемент не найден в течение таймаута — возвращаем False"):
                return False

    @allure.step("Проверка состояния кнопки «Добавить проект с задачами»")
    def is_button_enabled(self, selector: str) -> bool:
        """
        Проверяет, активна ли кнопка.
        Возвращает True, если кнопка активна (нет pointer-events-none),
        иначе False.
        """
        with allure.step(f"Поиск кнопки по XPath: {selector}"):
            btn = self.find_element_by_xpath(selector)

        with allure.step("Получение атрибута class кнопки"):
            classes = btn.get_attribute("class") or ""

        with allure.step(
                "Проверка отсутствия 'pointer-events-none' в классах"):
            return "pointer-events-none" not in classes

    @allure.step("Нажатие клавиши '{key_name}'")
    def press_key(self, key_name: str) -> None:
        """
        Имитирует нажатие управляющей клавиши.

        :param key_name: Название клавиши (регистронезависимо).
        Поддерживаются: ENTER, ESC, BACKSPACE.
        """

        key_map = {
            "ENTER": Keys.ENTER,
            "RETURN": Keys.RETURN,
            "ESC": Keys.ESCAPE,
            "ESCAPE": Keys.ESCAPE,
            "BACKSPACE": Keys.BACKSPACE,
            "BKSP": Keys.BACKSPACE,
        }

        key = key_name.upper()
        if key not in key_map:
            raise ValueError(
                f"Неизвестная клавиша '{key_name}'. "
                f"Используй одно из: {', '.join(key_map.keys())}"
            )

        with allure.step(f"Нажимаем: {key}"):
            ActionChains(self.browser).send_keys(key_map[key]).perform()
