import sys
import logging
import pandas as pd
from agents.arbitr_agent import ArbitrAgent
from agents.fed_resurs_agent import FedResursAgeng

from database import SessionLocal
from repository import Repository
from models.models import ElectronicCaseModel, BankruptcyStatementModel
from settings import configure_logging

logger = logging.getLogger(__name__)


def inspect_inns(
    fed_resurs_ageng: FedResursAgeng, inns: list[str]
) -> list[BankruptcyStatementModel]:
    """Формирует список объектов Сведений о банкротстве из списка ИНН команий"""
    rows = []

    for inn in inns:
        row = BankruptcyStatementModel()
        row.inn = inn
        card = fed_resurs_ageng.get_company_card_by_inn(inn)

        if card:
            guid = fed_resurs_ageng.parse_guid_from_company_card(card)

            if guid:
                case_info = fed_resurs_ageng.get_case_number(guid)

                if case_info:
                    case_number = fed_resurs_ageng.parse_case_number(case_info)
                    row.case_number = case_number

                case_date_info = fed_resurs_ageng.get_case_date_last(guid)

                if case_date_info and row.case_number:
                    last_date = fed_resurs_ageng.parse_case_date_last(case_date_info)
                    row.case_date_last = last_date

                rows.append(row)

    return rows


def inspect_documents(
    arbitr_agent: ArbitrAgent, bankruptcy_statements: list[BankruptcyStatementModel]
) -> list[ElectronicCaseModel]:
    """Формирует список объектов Электронные документы из списка документов"""
    rows = []

    for bankruptcy_statement in bankruptcy_statements:
        case_number = bankruptcy_statement.case_number

        if case_number:
            row = ElectronicCaseModel()
            row.case_number = case_number
            link = arbitr_agent.get_link_on_case_page(case_number)

            if link:
                case_id = arbitr_agent.get_case_id_by_link(link)
                document_info = arbitr_agent.get_case_documents(case_id)

                if document_info:

                    last_date = arbitr_agent.parse_case_date_last(document_info)
                    document_name = arbitr_agent.parse_case_document_name_last(
                        document_info
                    )

                    row.document_date_last = last_date if last_date else None
                    row.document_name = document_name if document_name else None

                    rows.append(row)
    return rows


def read_inn_from_excel(file_path: str) -> list[str]:
    """Чтение файла с ИНН"""
    try:
        df = pd.read_excel(file_path)

        inn_col = None
        for col in df.columns:
            if str(col).strip().lower() in ("inn", "инн", "идентификатор"):
                inn_col = col
                break

        if inn_col is None:
            inn_col = df.columns[0]

        inn_list = (
            df[inn_col].dropna().astype(str).str.strip().drop_duplicates().tolist()
        )
        return inn_list
    except Exception as exc:
        logger.exception("Reading file %r error" % file_path, exc_info=exc)


def main():
    configure_logging(level=logging.DEBUG)

    if len(sys.argv) < 2:
        logger.info("Use command: python main.py <path_to_file.xlsx>")
        sys.exit(1)

    excel_path = sys.argv[1]
    logger.info(f"Processing the file: {excel_path}")

    list_inn = read_inn_from_excel(excel_path)

    if list_inn:
        session = SessionLocal()
        repository = Repository(session)
        fed_resurs_ageng = FedResursAgeng()

        bankruptcy_statements = inspect_inns(fed_resurs_ageng, list_inn)

        if len(bankruptcy_statements) > 0:
            repository.create_bankruptcy_statements(bankruptcy_statements)

            arbitr_agent = ArbitrAgent()
            arbitr_agent.load_metadata()

            electronic_cases = inspect_documents(arbitr_agent, bankruptcy_statements)

            if len(electronic_cases) > 0:
                repository.create_electronic_cases(electronic_cases)

        repository.close()


if __name__ == "__main__":
    main()
