"""
Módulo responsável por gerenciar operações relacionadas a empresas.
"""

from typing import Union, List, Optional

from flambda_app.config import get_config
from flambda_app.logging import get_logger
from flambda_app.services.v1.company_service import CompanyService
from flambda_app.http_resources.request import ApiRequest
from flambda_app.vos.company import CompanyVO


class CompanyManager:
    """
    Classe responsável por gerenciar operações relacionadas a empresas.
    """

    def __init__(self, logger=None, config=None, company_service=None):
        """
        Inicializa a instância do CompanyManager.

        :param logger: Logger opcional, usa get_logger() por padrão.
        :param config: Configuração opcional, usa get_config() por padrão.
        :param company_service: Serviço de empresa opcional, usa CompanyService() por padrão.
        """
        self.logger = logger if logger is not None else get_logger()
        # configurations
        self.config = config if config is not None else get_config()
        # service
        self.company_service = company_service if company_service is not None else CompanyService(
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
        self.company_service.debug(self.debug_mode)

    def list(self, request: ApiRequest) -> List[Union[CompanyVO, dict]]:
        """
        Lista as empresas com base na requisição.

        :param request: Objeto de requisição.
        :return: Lista de empresas ou um dicionário vazio.
        """
        data = self.company_service.list(request.to_dict())
        if (data is None or len(data) == 0) and self.company_service.exception:
            self.exception = self.company_service.exception
            raise self.exception
        return data if data is not None else []

    def count(self, request: ApiRequest) -> int:
        """
        Obtém o total de empresas com base na requisição.

        :param request: Objeto de requisição.
        :return: Número total de empresas.
        """
        total = self.company_service.count(request.to_dict())
        if self.company_service.exception:
            self.exception = self.company_service.exception
            raise self.exception
        return total

    def get(self, request: ApiRequest, company_id: str) -> Optional[dict]:
        """
        Obtém uma empresa com base no ID.

        :param request: Objeto de requisição.
        :param company_id: ID da empresa.
        :return: Dados da empresa ou None.
        """
        data = self.company_service.get(request.to_dict(), company_id)
        if data is None and self.company_service.exception:
            self.exception = self.company_service.exception
            raise self.exception
        return data

    def create(self, request: ApiRequest) -> Optional[CompanyVO]:
        """
        Cria uma nova empresa com base na requisição.

        :param request: Objeto de requisição.
        :return: Objeto da empresa criada ou None.
        """
        data = self.company_service.create(request.to_dict())
        if (data is None) and self.company_service.exception:
            self.exception = self.company_service.exception
            raise self.exception
        return data

    def update(self, request: ApiRequest, company_id: str) -> Optional[dict]:
        """
        Atualiza uma empresa com base no ID.

        :param request: Objeto de requisição.
        :param company_id: ID da empresa.
        :return: Dados da empresa atualizada ou None.
        """
        data = self.company_service.update(request.to_dict(), company_id)
        if (data is None) and self.company_service.exception:
            self.exception = self.company_service.exception
            raise self.exception
        return data

    def delete(self, request: ApiRequest, company_id: str) -> bool:
        """
        Exclui uma empresa com base no ID.

        :param request: Objeto de requisição.
        :param company_id: ID da empresa.
        :return: True se a empresa foi excluída com sucesso, False caso contrário.
        """
        result = self.company_service.delete(request.to_dict(), company_id)
        if (result is None) and self.company_service.exception:
            self.exception = self.company_service.exception
            raise self.exception
        return result
