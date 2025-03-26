"""
Módulo responsável por gerenciar operações relacionadas a empresas.
"""

from typing import Union, List, NoReturn, Optional

from flambda_app import helper
from flambda_app.database.mysql import MySQLConnector
from flambda_app.database.redis import RedisConnector
from flambda_app.enums.messages import MessagesEnum
from flambda_app.exceptions import DatabaseException, ValidationException, ServiceException
from flambda_app.filter_helper import filter_xss_injection
from flambda_app.helper import get_function_name
from flambda_app.logging import get_logger
from flambda_app.repositories.v1.mysql.company_repository import CompanyRepository
from flambda_app.vos.company import CompanyVO


class CompanyService:
    """
    Camada de serviço para gerenciamento de operações da Empresa.
    """

    debug_mode = False
    REDIS_ENABLED = False

    def __init__(self, logger=None, mysql_connector=None, redis_connector=None,
                 company_repository=None):
        """
        Serviço para gerenciar operações relacionadas à empresa.

       Args:
           logger (Optional[Logger]): Instância do logger.
           mysql_connector (Optional[MySQLConnector]): Conector do MySQL.
           redis_connector (Optional[RedisConnector]): Conector do Redis.
           company_repository (Optional[CompanyRepository]): Repositório de empresas no MySQL.
       """
        # logger
        self.logger = logger if logger is None else get_logger()
        # database connection
        self.mysql_connector = mysql_connector if mysql_connector is not None else MySQLConnector()
        # mysql repository
        self.company_repository = company_repository if company_repository is not None \
            else CompanyRepository(mysql_connection=self.mysql_connector.get_connection())

        # exception
        self.exception = None

        if self.REDIS_ENABLED:
            # redis connection
            self.redis_connector = redis_connector if redis_connector is not None \
                else RedisConnector()
            # redis repository
            self.redis_company_repository = None

        self.debug(self.debug_mode)

    def debug(self, flag: bool = False):
        """
        Ativa ou desativa o modo de depuração.

        Args:
            flag (bool): Define se o modo de depuração será ativado ou desativado.
        """
        self.debug_mode = flag
        self.company_repository.debug = self.debug_mode
        if self.REDIS_ENABLED:
            self.redis_company_repository.debug = self.debug_mode

    def list(self, request_formatted: dict) -> List[Union[CompanyVO, dict]]:
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
        # if where == dict():
        #     where = {
        #         'active': 1
        #     }

        # exclude deleted
        where['deleted_at'] = None

        try:
            offset = request_formatted['offset']
            limit = request_formatted['limit']
            order_by = request_formatted['order_by']
            sort_by = request_formatted['sort_by']
            fields = request_formatted['fields']
            data = self.company_repository.list(
                where=where, offset=offset, limit=limit, order_by=order_by,
                sort_by=sort_by, fields=fields)

            # convert to vo and prepare for api response
            if data:
                data = [CompanyVO(**item).to_api_response() for item in data]

            # set exception if it happens
            if self.company_repository.get_exception():
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
        if where == dict():
            where = {
                'active': 1
            }

        # exclude deleted
        where['deleted_at'] = None

        try:
            order_by = request['order_by']
            sort_by = request['sort_by']
            total = self.company_repository.count(
                where=where, order_by=order_by, sort_by=sort_by)

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

    def find(self, request: dict) -> NoReturn:
        """
        Método não implementado para busca de empresas.

        Args:
            request (dict): Parâmetros da requisição.

        Raises:
            ServiceException: Exceção indicando que o método não foi implementado.
        """
        self.logger.info('method: {} - request: {}'
                         .format(get_function_name(), request))
        raise ServiceException(MessagesEnum.METHOD_NOT_IMPLEMENTED_ERROR)

    def get(self, request_formatted: dict, company_id: str) -> Optional[dict]:
        """
        Obtém os dados de uma empresa com base no ID.

        Args:
            request_formatted (dict): Parâmetros da requisição formatados.
            company_id (str): ID da empresa.

        Returns:
            Optional[dict]: Dados da empresa ou None se não encontrada.
        """
        self.logger.info('method: {} - request: {}'
                         .format(get_function_name(), request_formatted))

        self.logger.info('method: {} - uuid: {}'
                         .format(get_function_name(), company_id))

        data = []
        where = request_formatted['where']

        try:
            fields = request_formatted['fields']
            value = company_id
            data = self.company_repository.get(
                value, key=self.company_repository.PK, where=where, fields=fields
            )

            if self.debug_mode:
                self.logger.info('data: {}'.format(data))

            # convert to vo and prepare for api response
            if data and isinstance(data, dict):
                data = CompanyVO(**data).to_api_response()

            # set exception if it happens
            if self.company_repository.get_exception():
                raise DatabaseException(MessagesEnum.FIND_ERROR)

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

    def create(self, request_formatted: dict) -> Optional[CompanyVO]:
        """
        Cria uma nova empresa.

        Args:
            request_formatted (dict): Dados formatados para criação da empresa.

        Returns:
            Optional[CompanyVO]: Objeto da empresa criada ou None em caso de erro.
        """
        self.logger.info('method: {} - request: {}'.format(
            get_function_name(), request_formatted))

        data = request_formatted['where']
        if self.debug_mode:
            self.logger.info('method: {} - data: {}'.format(get_function_name(), data))

        try:

            if data == dict():
                raise ValidationException(MessagesEnum.REQUEST_ERROR)

            company_vo = CompanyVO(**data)
            created = self.company_repository.create(company_vo)

            if not created:
                raise DatabaseException(MessagesEnum.CREATE_ERROR)

            return company_vo

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

    def update(self, request_formatted: dict, uuid) -> Optional[dict]:
        """
        Atualiza uma empresa existente.

        Args:
            request_formatted (dict): Dados formatados para atualização da empresa.
            uuid: Identificador único da empresa.

        Returns:
            Optional[dict]: Dados atualizados da empresa ou None em caso de erro.
        """
        self.logger.info('method: {} - request: {}'.format(
            get_function_name(), request_formatted))

        original_company = self.company_repository.get(uuid, key=self.company_repository.PK)
        if original_company is None:
            raise DatabaseException(MessagesEnum.FIND_ERROR)

        data = request_formatted['where']
        if self.debug_mode:
            self.logger.info('method: {} - data: {}'.format(get_function_name(), data))

        # validate the request payload
        self.validate_data(data, original_company)

        # update original company with update data
        original_company.update(data)

        data = original_company

        try:

            if data == dict():
                raise ValidationException(MessagesEnum.REQUEST_ERROR)

            # updated_at = helper.datetime_now_with_timezone()
            updated_at = helper.datetime_now_with_timezone().replace(tzinfo=None).isoformat(sep=' ')

            data.update({'updated_at': updated_at})

            company_vo = data

            updated = self.company_repository.update(company_vo, uuid,
                                                     key=self.company_repository.PK)

            if updated:
                # convert to vo and prepare for api response
                data = company_vo.to_api_response()
            else:
                data = None
                # set exception if it happens
                raise DatabaseException(MessagesEnum.UPDATE_ERROR)

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

    def delete(self, request_formatted: dict, company_id: str) -> bool:
        """
        Exclui logicamente uma empresa.

        Args:
            request_formatted (dict): Dados formatados da requisição.
            company_id (str): Identificador único da empresa.

        Returns:
            bool: True se a exclusão for bem-sucedida, False caso contrário.
        """
        self.logger.info('method: {} - request: {}'.format(
            get_function_name(), request_formatted))
        result = False

        original_company = self.company_repository.get(company_id, key=self.company_repository.PK)
        if original_company is None:
            raise DatabaseException(MessagesEnum.FIND_ERROR)

        try:

            updated = self.company_repository.soft_delete(value=company_id,
                                                          key=self.company_repository.PK)

            if updated:
                result = True
            else:
                # set exception if it happens
                raise DatabaseException(MessagesEnum.SOFT_DELETE_ERROR)

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

        return result

    def validate_data(self, data, original_company):
        """
        Valida os dados da empresa antes da atualização.

        Args:
            data (dict): Dados fornecidos para atualização.
            original_company: Instância original da empresa.

        Raises:
            ValidationException: Se algum campo inválido for encontrado.
        """
        allowed_fields = list(original_company.to_dict().keys())
        try:
            allowed_fields.remove(self.company_repository.UUID_KEY)
            allowed_fields.remove(self.company_repository.PK)
            allowed_fields.remove('updated_at')
            allowed_fields.remove('created_at')
            allowed_fields.remove('deleted_at')

        except KeyError as err:
            self.logger.error(f"Erro ao acessar chave do dicionário: {err}")
            self.exception = err

        except DatabaseException as err:
            self.logger.error(f"Erro no banco de dados: {err}")
            self.exception = err

        except Exception as err:
            self.logger.exception(f"Erro inesperado: {err}")
            self.exception = err
            self.logger.error(err)
            raise

        fields = list(data.keys())
        for field in fields:
            if field not in allowed_fields:
                exception = ValidationException(MessagesEnum.VALIDATION_ERROR)
                exception.params = [filter_xss_injection(data[field]), filter_xss_injection(field)]
                exception.set_message_params()
                raise exception
