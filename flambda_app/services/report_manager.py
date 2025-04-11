"""
Módulo responsável por gerenciar operações relacionadas a empresas.
"""

from typing import Union, List

from flambda_app.config import get_config
from flambda_app.logging import get_logger
from flambda_app.services.v1.report_service import ReportService
from flambda_app.http_resources.request import ApiRequest
from flambda_app.vos.report import Report, ReportType


class ReportManager:
    """
    Classe responsável por gerenciar operações relacionadas a empresas.
    """

    def __init__(self, logger=None, config=None, report_service=None):
        """
        Inicializa a instância do CompanyManager.

        :param logger: Logger opcional, usa get_logger() por padrão.
        :param config: Configuração opcional, usa get_config() por padrão.
        :param report_service: Serviço de report opcional, usa CompanyService() por padrão.
        """
        self.logger = logger if logger is not None else get_logger()
        # configurations
        self.config = config if config is not None else get_config()
        # service
        self.report_service = report_service if report_service is not None else ReportService(
            self.logger)

        # exception
        self.exception = None

        # debug
        self.debug_mode = None

    def debug(self, flag: bool = False):
        """
       Define o modo de depuração.

       :param flag: Se True, ativa o modo de depuração.
       """
        self.debug_mode = flag
        self.report_service.debug(self.debug_mode)

    def count(self, request: ApiRequest) -> int:
        """
        Obtém o total de report com base na requisição.

        :param request: Objeto de requisição.
        :return: Número total de empresas.
        """
        total = self.report_service.count(request.to_dict())
        if self.report_service.exception:
            self.exception = self.report_service.exception
            raise self.exception
        return total

    def list_report_type(self, request: ApiRequest) -> List[Union[ReportType, dict]]:
        """
        Lista os report type com base na requisição.

        :param request: Objeto de requisição.
        :return: Lista de report type ou um dicionário vazio.
        """
        data = self.report_service.list_report_type(request.to_dict())
        if (data is None or len(data) == 0) and self.report_service.exception:
            self.exception = self.report_service.exception
            raise self.exception
        return data if data is not None else []

    def list(self, request: ApiRequest) -> List[Union[Report, dict]]:
        """
        Lista os report type com base na requisição.

        :param request: Objeto de requisição.
        :return: Lista de report type ou um dicionário vazio.
        """
        data = self.report_service.list(request.to_dict())
        if (data is None or len(data) == 0) and self.report_service.exception:
            self.exception = self.report_service.exception
            raise self.exception
        return data if data is not None else []
