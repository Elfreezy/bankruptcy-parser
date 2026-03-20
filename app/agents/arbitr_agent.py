import logging

from datetime import datetime
from bs4 import BeautifulSoup

from agents.base_user_agent import BaseUserAgent


logger = logging.getLogger(__name__)


class ArbitrAgent(BaseUserAgent):
    """Агент работы с сервисом kad.arbitr"""

    def __init__(
        self,
        base_url: str = "https://kad.arbitr.ru",
        referer: str = "https://kad.arbitr.ru",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:148.0) Gecko/20100101 Firefox/148.0",
        accept="application/json, text/plain, */*",
        accept_language="ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    ):
        super().__init__(
            referer=referer,
            user_agent=user_agent,
            accept=accept,
            accept_language=accept_language,
        )

        self.base_url = base_url
        self.set_proxy: bool = True
        self.set_cookies: bool = True
        self.set_header: bool = True

    def load_metadata(
        self,
    ):
        """Загрузка метаданных для корректного парсинга"""
        if self.set_header:
            self.load_headers()
        if self.set_proxy:
            self.change_current_proxy(self.base_url)
        if self.set_cookies:
            self.load_need_cookies()

    def load_headers(self):
        headers = {
            "X-Requested-With": "XMLHttpRequest",
        }

        self.add_headers(headers)

    def load_need_cookies(
        self,
        need_cookie: list[str] = ["pr_fp", "wasm"],
        is_need_click: bool = True,
        btn_selector_click: str = "//div[@id='b-form-submit']",
    ):
        """Присвоение необходимых кук"""
        cookies = self.get_cookie(
            self.base_url,
            need_cookie,
            is_need_click=is_need_click,
            btn_selector_click=btn_selector_click,
        )
        self.cookies = cookies

    def get_link_on_case_page(
        self,
        case: str,
        sufix_url: str = "/Kad/SearchInstances",
        page: int = 1,
        count: int = 25,
    ):
        """Метод возвращает ссылку на дело"""
        json_data = {
            "Page": page,
            "Count": count,
            "CaseNumbers": [
                case,
            ],
        }

        try:
            target_url = "%s/%s" % (self.base_url, sufix_url)
            logger.debug("Request to %r with cookie %r" % (target_url, self.cookies))

            querty_params = {
                "cookies": self.cookies,
                "json": json_data,
            }

            response_data = self.get_response(
                url=target_url,
                method="POST",
                querty_params=querty_params,
            ).text

            link = self.extract_link_from_html(
                html=response_data, selector="a.num_case"
            )
            return link

        except Exception as exc:
            logger.exception("Extract link error", exc_info=exc)

    def get_case_id_by_link(self, link: str) -> str | None:
        """Метод возвращает id дела из ссылки"""
        try:
            case_id = link.split("/")[-1]
            return case_id
        except Exception as exc:
            logger.debug("Invalid link structure %r" % link)

    def get_case_documents(
        self,
        case_id: str,
        sufix_url: str = "Kad/CaseDocumentsPage",
        page: int = 1,
        per_page: int = 1,
    ):
        """Метод возвращает электронные документы закрепленные за делом"""
        params = {
            "caseId": case_id,
            "page": page,
            "perPage": per_page,
        }

        try:
            target_url = "%s/%s" % (self.base_url, sufix_url)
            logger.debug("Request to %r with cookie %r" % (target_url, self.cookies))

            querty_params = {
                "cookies": self.cookies,
                "params": params,
            }

            response = self.get_response(
                url=target_url,
                method="GET",
                querty_params=querty_params,
            )

            return self.get_data_json(response)

        except Exception as exc:
            logger.exception(exc_info=exc)

    def parse_case_date_last(self, document_info: dict) -> str:
        """Извлечение последней даты из информации по документу"""
        last_date = None
        try:
            last_date_str = (
                document_info.get("Result", {}).get("Items", {})[0].get("DisplayDate")
            )
            last_date = datetime.strptime(last_date_str, "%d.%m.%Y").isoformat()
        except Exception as exc:
            logger.debug("Invalid case date info structure", exc_info=exc)

        return last_date

    def parse_case_document_name_last(self, document_info: dict) -> str:
        """Извлечение наименования документа из информации по документу"""
        document_name = None
        try:
            document_name = (
                document_info.get("Result", {})
                .get("Items", {})[0]
                .get("ContentTypes")[0]
            )
        except Exception as exc:
            logger.debug("Invalid case date info structure", exc_info=exc)

        return document_name

    def extract_link_from_html(
        self,
        html: str,
        selector: str,
    ) -> str:
        """Извлечение ссылки на дело из объекта HTML"""
        soup = BeautifulSoup(html, "html.parser")
        element = soup.select_one(selector)
        return element["href"] if element and "href" in element.attrs else None


## 65.21.201.149:8080 <Response [200]>
arbitr_agent = ArbitrAgent()
# arbitr_agent.is_mock_proxy = True
# arbitr_agent.load_metadata()
# document = arbitr_agent.get_case_documents()
# logger.info(document)


# filtered_proxies = arbitr_agent.filter_proxies(arbitr_agent.base_url, proxies)
# logger.info(filtered_proxies)
