import logging
from sqlalchemy.orm import Session
from models.models import BankruptcyStatementModel, ElectronicCaseModel

logger = logging.getLogger(__name__)


class Repository:

    def __init__(self, session: Session):
        self.session = session

    def create_bankruptcy_statement(
        self, bankruptcy_statement: BankruptcyStatementModel
    ) -> BankruptcyStatementModel | None:
        try:
            self.session.add(bankruptcy_statement)
            self.session.commit()
        except Exception as exc:
            self.session.rollback()
            logger.exception("DB exception", exc_info=exc)

    def create_electronic_case(
        self, electronic_case: ElectronicCaseModel
    ) -> ElectronicCaseModel | None:
        try:
            self.session.add(electronic_case)
            self.session.commit()
        except Exception as exc:
            self.session.rollback()
            logger.exception("DB exception", exc_info=exc)

    def create_bankruptcy_statements(
        self, bankruptcy_statements: list[BankruptcyStatementModel]
    ) -> BankruptcyStatementModel | None:
        try:
            self.session.add_all(bankruptcy_statements)
            self.session.commit()
        except Exception as exc:
            self.session.rollback()
            logger.exception("DB exception", exc_info=exc)

    def create_electronic_cases(
        self, electronic_cases: list[ElectronicCaseModel]
    ) -> ElectronicCaseModel | None:
        try:
            self.session.add_all(electronic_cases)
            self.session.commit()
        except Exception as exc:
            self.session.rollback()
            logger.exception("DB exception", exc_info=exc)

    def close(self):
        if self.session.is_active:
            self.session.close()
