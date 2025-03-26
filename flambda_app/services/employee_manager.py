"""
Módulo responsável por gerenciar operações relacionadas ao funcionario.
"""

from typing import Dict, Any, List, Optional

from flambda_app.config import get_config
from flambda_app.http_resources.response import ApiResponse
from flambda_app.logging import get_logger
from flambda_app.services.v1.employee_service import EmployeeService
from flambda_app.vos.employee import EmployeeVO


class EmployeeManager:
    """
    Classe responsável por gerenciar operações relacionadas aos funcionarios.
    """

    def __init__(self, logger=None, config=None, employee_service=None):
        """
        Inicializa o gerenciador de funcionários.

        :param logger: Instância do logger, opcional.
        :param config: Configurações da aplicação, opcional.
        :param employee_service: Serviço de funcionários, opcional.
        """
        self.logger = logger if logger is not None else get_logger()
        # configurations
        self.config = config if config is not None else get_config()
        # service
        self.employee_service = employee_service if employee_service is not None \
            else EmployeeService(self.logger)

        # exception
        self.exception = None

        # debug
        self.DEBUG = None

    def debug(self, flag: bool = False):
        """
       Define o modo de depuração.

       :param flag: Se True, ativa o modo de depuração.
       """
        self.DEBUG = flag
        self.employee_service.debug(self.DEBUG)

    def list(self, request: ApiResponse) -> List[Dict[str, Any]]:
        """
        Retorna a lista de funcionários com base na requisição.

        :param request: Objeto de requisição.
        :return: Lista de funcionários como dicionários.
        :raises Exception: Se ocorrer um erro no serviço.
        """
        data = self.employee_service.list(request.to_dict())
        if (data is None or len(data) == 0) and self.employee_service.exception:
            self.exception = self.employee_service.exception
            raise self.exception
        return data

    def count(self, request: ApiResponse) -> int:
        """
        Retorna a quantidade de funcionários com base na requisição.

        :param request: Objeto de requisição.
        :return: Número total de funcionários.
        :raises Exception: Se ocorrer um erro no serviço.
        """
        total = self.employee_service.count(request.to_dict())
        if self.employee_service.exception:
            self.exception = self.employee_service.exception
            raise self.exception
        return total

    def get(self, request: ApiResponse, employee_id: str) -> Dict[str, Any]:
        """
        Obtém um funcionário com base no ID.

        :param request: Objeto de requisição.
        :param employee_id: ID do funcionário.
        :return: Dados do funcionário.
        :raises Exception: Se ocorrer um erro no serviço.
        """
        data = self.employee_service.get(request.to_dict(), employee_id)
        if (data is None) and self.employee_service.exception:
            self.exception = self.employee_service.exception
            raise self.exception
        return data

    def create(self, request: ApiResponse) -> Optional[EmployeeVO]:
        """
        Cria um novo funcionário.

        :param request: Objeto de requisição.
        :return: Objeto EmployeeVO ou None.
        :raises Exception: Se ocorrer um erro no serviço.
        """
        data = self.employee_service.create(request.to_dict())
        if (data is None) and self.employee_service.exception:
            self.exception = self.employee_service.exception
            raise self.exception
        return data

    def update(self, request: ApiResponse, employee_id: str) -> Optional[dict]:
        """
        Atualiza os dados de um funcionário.

        :param request: Objeto de requisição.
        :param employee_id: ID do funcionário.
        :return: Dados atualizados do funcionário ou None.
        :raises Exception: Se ocorrer um erro no serviço.
        """
        data = self.employee_service.update(request.to_dict(), employee_id)
        if (data is None) and self.employee_service.exception:
            self.exception = self.employee_service.exception
            raise self.exception
        return data

    def delete(self, request: ApiResponse, employee_id: str) -> bool:
        """
        Exclui um funcionário com base no ID.

        :param request: Objeto de requisição.
        :param employee_id: ID do funcionário.
        :return: True se a exclusão for bem-sucedida, False caso contrário.
        :raises Exception: Se ocorrer um erro no serviço.
        """
        result = self.employee_service.delete(request.to_dict(), employee_id)
        if (result is None) and self.employee_service.exception:
            self.exception = self.employee_service.exception
            raise self.exception
        return result
