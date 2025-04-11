"""
Módulo responsável por gerenciar operações relacionadas ao report.
"""

from typing import Union, List

from flambda_app.database.mysql import MySQLConnector
from flambda_app.database.redis import RedisConnector
from flambda_app.enums.messages import MessagesEnum
from flambda_app.exceptions import DatabaseException
from flambda_app.helper import get_function_name
from flambda_app.logging import get_logger
from flambda_app.repositories.v1.mysql.report_repository import ReportRepository
from flambda_app.vos.report import Report, ReportType


class ReportService:
    """
    Camada de serviço para gerenciamento de operações da Empresa.
    """

    debug_mode = False
    REDIS_ENABLED = False

    def __init__(self, logger=None, mysql_connector=None, redis_connector=None,
                 report_repository=None):
        """
        Serviço para gerenciar operações relacionadas à empresa.

       Args:
           logger (Optional[Logger]): Instância do logger.
           mysql_connector (Optional[MySQLConnector]): Conector do MySQL.
           redis_connector (Optional[RedisConnector]): Conector do Redis.
           report_repository (Optional[ReportRepository]): Repositório de empresas no MySQL.
       """
        # logger
        self.logger = logger if logger is None else get_logger()
        # database connection
        self.mysql_connector = mysql_connector if mysql_connector is not None else MySQLConnector()
        # mysql repository
        self.report_repository = report_repository if report_repository is not None \
            else ReportRepository(mysql_connection=self.mysql_connector.get_connection())

        # exception
        self.exception = None

        if self.REDIS_ENABLED:
            # redis connection
            self.redis_connector = redis_connector if redis_connector is not None \
                else RedisConnector()
            # redis repository
            self.redis_report_repository = None

        self.debug(self.debug_mode)

    def debug(self, flag: bool = False):
        """
        Ativa ou desativa o modo de depuração.

        Args:
            flag (bool): Define se o modo de depuração será ativado ou desativado.
        """
        self.debug_mode = flag
        self.report_repository.debug = self.debug_mode
        if self.REDIS_ENABLED:
            self.redis_report_repository.debug = self.debug_mode

    def count(self, request: dict) -> int:
        """
        Conta o número de empresas com base nos filtros fornecidos.

        Args:
            request (dict): Filtros e parâmetros da consulta.

        Returns:
            int: Total de empresas encontradas.
        """
        self.logger.info('method: {} - request: {}'
                         .format(get_function_name(), request))

        total: int = 0
        where = request['where']

        # exclude deleted
        where['deleted_at'] = None

        try:
            order_by = request['order_by']
            sort_by = request['sort_by']
            total = self.report_repository.count(where=where,
                                                 order_by=order_by,
                                                 sort_by=sort_by,
                                                 base_table='report_type',
                                                 base_table_alias='rt')

        except KeyError as err:
            self.logger.error(f"Erro ao acessar chave do dicionário: {err}")
            self.exception = err

        except DatabaseException as err:
            self.logger.error(f"Erro no banco de dados: {err}")
            self.exception = err

        except Exception as err:
            self.logger.error(err)
            self.exception = DatabaseException(MessagesEnum.LIST_ERROR)
            raise

        return total

    def list_report_type(self, request_formatted: dict) -> List[Union[ReportType, dict]]:
        """
        Lista as empresas com base nos filtros fornecidos.

        Args:
            request_formatted (dict): Filtros e parâmetros da consulta.

        Returns:
            List[Union[CompanyVO, dict]]: Lista de empresas formatadas para resposta da API.
        """
        self.logger.info('method: {} - request: {}'.format(
            get_function_name(), request_formatted))

        data = []
        where = request_formatted['where']

        # exclude deleted
        where['deleted_at'] = None

        try:
            offset = request_formatted['offset']
            limit = request_formatted['limit']
            order_by = request_formatted['order_by']
            sort_by = request_formatted['sort_by']
            fields = request_formatted['fields']
            data = self.report_repository.list(
                where=where, offset=offset, limit=limit, order_by=order_by,
                sort_by=sort_by, fields=fields, base_table='report_type', base_table_alias='rt')

            if data:
                data = [ReportType(**item).to_api_response() for item in data]

            # set exception if it happens
            if self.report_repository.get_exception():
                raise DatabaseException(MessagesEnum.LIST_ERROR)

        except KeyError as err:
            self.logger.error(f"Erro ao acessar chave do dicionário: {err}")
            self.exception = err

        except DatabaseException as err:
            self.logger.error(f"Erro no banco de dados: {err}")
            self.exception = err

        except Exception as err:
            self.logger.exception(f"Erro inesperado: {err}")
            self.exception = err
            raise

        return data

    def list(self, request_formatted: dict) -> List[Union[Report, dict]]:
        """
        Lista os relatorios com base nos filtros fornecidos.

        Args:
            request_formatted (dict): Filtros e parâmetros da consulta.

        Returns:
            List[Union[Report, dict]]: Lista de empresas formatadas para resposta da API.
        """
        self.logger.info('method: {} - request: {}'.format(
            get_function_name(), request_formatted))

        data = []
        where = request_formatted['where']

        # exclude deleted
        where['deleted_at'] = None

        try:
            offset = request_formatted['offset']
            limit = request_formatted['limit']
            order_by = request_formatted['order_by']
            sort_by = request_formatted['sort_by']
            fields = request_formatted['fields']
            data = self.report_repository.list(
                where=where, offset=offset, limit=limit, order_by=order_by,
                sort_by=sort_by, fields=fields, base_table='reports', base_table_alias='r')

            if data:
                data = [Report(**item).to_api_response() for item in data]

            # set exception if it happens
            if self.report_repository.get_exception():
                raise DatabaseException(MessagesEnum.LIST_ERROR)

        except KeyError as err:
            self.logger.error(f"Erro ao acessar chave do dicionário: {err}")
            self.exception = err

        except DatabaseException as err:
            self.logger.error(f"Erro no banco de dados: {err}")
            self.exception = err

        except Exception as err:
            self.logger.exception(f"Erro inesperado: {err}")
            self.exception = err
            raise

        return data
