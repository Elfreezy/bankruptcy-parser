import logging

from requests import Response

from agents.base_user_agent import BaseUserAgent

logger = logging.getLogger(__name__)


class FedResursAgeng(BaseUserAgent):
    """Агент работы с сервисом fedresurs"""

    def __init__(
        self,
        base_url: str = "https://fedresurs.ru/backend/companies",
        referer: str = "https://fedresurs.ru/",
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

    def get_company_card_by_inn(
        self, inn: str, limit: int = 15, offset: int = 0, is_active: str = "true"
    ) -> dict | None:
        """Метод возвращает карточку дела по ИНН компании"""
        params = {
            "searchString": inn,
            "limit": limit,
            "offset": offset,
            "isActive": is_active,
        }

        querty_params = {
            "params": params,
        }

        response = self.get_response(self.base_url, "GET", querty_params=querty_params)
        return self.get_data_json(response)

    def get_case_number(
        self,
        guid: str,
        url_suffix: str = "bankruptcy",
    ) -> dict | None:
        """Метод возвращает номер дела из карточки дела"""
        target_url = "%s/%s/%s" % (self.base_url, guid, url_suffix)

        response = self.get_response(target_url, "GET")

        return self.get_data_json(response)

    def get_case_date_last(
        self,
        guid: str,
        url_suffix: str = "publications",
        limit: int = 15,
        offset: int = 0,
    ) -> dict | None:
        """Метод возвращает последнюю дату документов о банкротстве из карточки дела"""
        params = {
            "limit": limit,
            "offset": offset,
        }

        querty_params = {
            "params": params,
        }

        target_url = "%s/%s/%s" % (self.base_url, guid, url_suffix)
        response = self.get_response(target_url, "GET", querty_params)

        return self.get_data_json(response)

    def parse_guid_from_company_card(self, company_card: dict) -> str:
        """Парсит json ответ в поисках информации о GUID компании"""
        guid = None
        try:
            guid = company_card.get("pageData", {})[0].get("guid")
        except Exception as exc:
            logger.debug("Invalid card structure", exc_info=exc)

        return guid

    def parse_case_number(self, case_info: dict) -> str:
        """Парсит json ответ в поисках информации о номере дела"""
        number = None
        try:
            number = case_info.get("legalCases", {})[0].get("number")
        except Exception as exc:
            logger.debug("Invalid case info structure", exc_info=exc)

        return number

    def parse_case_date_last(self, case_date_info: dict) -> str:
        """Парсит json ответ в поисках информации даты последней публикации по делу"""
        number = None
        try:
            number = case_date_info.get("pageData", {})[0].get("datePublish")
        except Exception as exc:
            logger.debug("Invalid case date info structure", exc_info=exc)

        return number


def main():
    fed_resurs_ageng = FedResursAgeng()
    # card = fed_resurs_ageng.get_company_card_by_inn("1621004803")
    # logger.info(card)
    guid = "c15a8e4b-fca4-456a-9c9c-a54c28c3eb9c"
    # tttt = fed_resurs_ageng.get_case_number("c15a8e4b-fca4-456a-9c9c-a54c28c3eb9c")
    # logger.info(tttt)
    # case_info = fed_resurs_ageng.get_case_number(guid)
    # case_number = fed_resurs_ageng.parse_case_number(case_info)
    # logger.info(case_number)
    case_date_info = fed_resurs_ageng.get_case_date_last(guid)
    last_date = fed_resurs_ageng.parse_case_date_last(case_date_info)
    logger.info(last_date)


if __name__ == "__main__":
    main()
