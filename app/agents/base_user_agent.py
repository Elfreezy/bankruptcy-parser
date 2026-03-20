import time
import requests
import logging
import random
from seleniumbase import SB
from requests import Response
from bs4 import BeautifulSoup
from requests.exceptions import ReadTimeout

logger = logging.getLogger(__name__)


class BaseUserAgent:

    def __init__(
        self,
        referer: str,
        user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:148.0) Gecko/20100101 Firefox/148.0",
        accept: str = "application/json, text/plain, */*",
        accept_language: str = "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    ):
        self.headers = {
            "User-Agent": user_agent,
            "Accept": accept,
            "Accept-Language": accept_language,
            "Referer": referer,
        }

        self.proxy = {}
        self.cookies = {}
        self.filtered_proxies = []

        self.is_mock_proxy: bool = True
        self.is_mock_cookie: bool = True

    def add_headers(self, headers: dict) -> None:
        for key, value in headers.items():
            self.headers[key] = value

    def get_data_json(self, response: Response) -> dict | None:
        try:
            response_data = response.json()
            return response_data
        except Exception as exc:
            logger.exception("Invalid json structure by response", exc_info=exc)
        return None

    def get_response(
        self,
        url: str,
        method: str,
        querty_params: dict = {},
        retry: int = 5,
        delay: int = 1,
    ) -> Response | None:

        for i in range(1, retry + 1):
            time.sleep(delay)
            try:
                if method == "POST":
                    response = requests.post(
                        headers=self.headers,
                        url=url,
                        **querty_params,
                    )
                else:
                    response = requests.get(
                        headers=self.headers,
                        url=url,
                        **querty_params,
                    )

                logger.debug(
                    "### Requests to %r, status_code: %r, querty_params: %r"
                    % (url, response.status_code, querty_params)
                )

                response.raise_for_status()

                return response

            except Exception as exc:
                logger.exception(
                    "Invalid trying %d/%d for url:%r, querty_params: %r"
                    % (i, retry, url, querty_params),
                    exc_info=exc,
                )

    def get_cookie(
        self,
        url: str,
        cookies_name: list[str],
        retry: int = 5,
        delay: int = 10,
        is_need_click: bool = False,
        btn_selector_click: str = None,
        time_limit: int = 120,
    ):
        """Смена прокси при ошибке"""

        if self.is_mock_cookie:
            return {
                "pr_fp": "2e6d70eb9247687ef61ae3f1950ed50971fe935d63982f7ef4dde794dbdcdc98",
                "wasm": "53bc69d560d077b15c1f5a7e165f39e8",
            }

        returned_cookies = {}

        for i in range(1, retry + 1):
            time.sleep(delay)
            try:
                with SB(
                    uc=True,
                    headed=True,
                    time_limit=time_limit,
                    # disable_js=True,
                    # block_images=True,
                    # proxy=self.proxy,
                ) as driver:
                    driver.get(url)

                    if is_need_click:
                        time.sleep(delay)
                        driver.click_xpath(btn_selector_click)

                    time.sleep(delay)

                    cookies = driver.get_cookies()
                    for cookie in cookies:
                        if cookie.get("name") in cookies_name:
                            returned_cookies[cookie.get("name")] = cookie.get("value")
                    break
            except Exception as exc:
                logger.info(
                    "%d / %d Faild try to get cookies %r. Proxy is %r"
                    % (i, retry, url, self.proxy),
                    exc_info=exc,
                )

        if len(returned_cookies) == 0:
            logger.info("Cookies not found for %r" % url)

        logger.debug("### Returned cookies: %r" % returned_cookies)
        return returned_cookies

    def get_free_proxies(
        self,
        url: str = "https://free-proxy-list.net/",
        start_index: int = 0,
        count: int = 30,
    ):
        """Возвращает список бесплатных proxy"""
        proxies = None

        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")

            proxies = []
            table = soup.find("table", class_="table")
            rows = table.find_all("tr")[start_index : start_index + count]

            for row in rows:
                cols = row.find_all("td")
                if len(cols) > 1:
                    ip = cols[0].text.strip()
                    port = cols[1].text.strip()
                    proxy = f"{ip}:{port}"
                    proxies.append(proxy)
        except Exception as exc:
            logger.debug("Faild getting proxy proccess", exc_info=exc)

        return proxies

    def filter_proxies(
        self, url: str, proxy_list: list[str], timeout: int = 10, delay: int = 1
    ):
        """Возвращает список proxy, которые доступны для сервиса"""
        filtered_proxies = []

        for proxy in proxy_list:
            time.sleep(delay)
            try:
                proxies = {
                    "http": proxy,
                    "https": proxy,
                }
                response = requests.get(
                    url,
                    proxies=proxies,
                    timeout=timeout,
                )

                if response.status_code == 200:
                    filtered_proxies.append(proxy)

            except Exception as exc:
                logger.debug("Faild get filtered proxy proccess", exc_info=exc)

        return filtered_proxies

    def change_filtered_proxies(
        self,
        url: str,
        retry: int = 5,
    ) -> None:

        if self.is_mock_proxy:
            proxies = [
                "113.160.132.26:8080",
                "137.220.150.152:6005",
                "38.34.179.190:8450",
                "85.198.96.242:3128",
                "103.133.26.117:8080",
                "137.220.151.110:6005",
                "137.220.150.104:6005",
                "202.155.12.161:443",
            ]
            self.filtered_proxies = proxies
            return None

        for _ in range(retry):
            proxies = self.get_free_proxies(
                start_index=random.randint(0, 200), count=random.randint(10, 50)
            )
            self.filtered_proxies = self.filter_proxies(url, proxies)

            if len(self.filtered_proxies) > 0:
                break

    def change_current_proxy(
        self,
        url: str,
        retry: int = 5,
    ) -> None:
        logger.debug("### Change current proxy %r" % self.proxy)
        if len(self.filtered_proxies) == 0:
            self.change_filtered_proxies(url, retry)

        logger.debug("### Filtered_proxies: %r" % self.filtered_proxies)
        self.proxy = self.filtered_proxies.pop(0)
        logger.debug("### New current proxy: %r" % self.proxy)


def main():
    user_agent = BaseUserAgent(referer="https://kad.arbitr.ru/")
    logger.info(
        user_agent.get_coockie(
            "https://kad.arbitr.ru/",
            ["pr_fp", "wasm"],
            is_need_click=True,
            btn_selector_click="//div[@id='2b-form-submit']",
        )
    )


if __name__ == "__main__":
    main()
