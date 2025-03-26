"""
Módulo responsável por gerenciar operações relacionadas ao funcionario.
"""

from typing import Dict, Any, Optional, List, NoReturn

from flambda_app import helper
from flambda_app.database.mysql import MySQLConnector
from flambda_app.database.redis import RedisConnector
from flambda_app.enums.messages import MessagesEnum
from flambda_app.exceptions import DatabaseException, ValidationException, ServiceException
from flambda_app.filter_helper import filter_xss_injection
from flambda_app.helper import get_function_name
from flambda_app.logging import get_logger
from flambda_app.repositories.v1.mysql.employee_respository import EmployeeRepository
from flambda_app.vos.employee import EmployeeVO


class EmployeeService:
    """
    Serviço responsável pela lógica de negócios relacionada a funcionários (Employees).

    Gerencia a comunicação com repositórios de banco de dados e cache Redis,
    além de lidar com exceções e logs.

    Atributos:
        DEBUG (bool): Define se o modo de depuração está ativado.
        REDIS_ENABLED (bool): Define se a integração com Redis está ativada.
        logger (Logger): Logger para registrar informações e erros do serviço.
        mysql_connector (MySQLConnector): Conector para acesso ao banco de dados MySQL.
        redis_connector (RedisConnector, opcional): Conector para acesso ao Redis (caso ativado).
        employee_repository (EmployeeRepository): Repositório para operações no banco de dados.
        redis_employee_repository (RedisEmployeeRepository, opcional): Repositório para cache Redis.
        exception (Exception, opcional): Armazena exceções capturadas durante operações.
    """
    DEBUG = False
    REDIS_ENABLED = False

    def __init__(self, logger=None, mysql_connector=None, redis_connector=None,
                 employee_repository=None):
        """
        Inicializa o EmployeeService, configurando conexões com banco de dados e cache.
        """
        # logger
        self.logger = logger if logger is None else get_logger()
        # database connection
        self.mysql_connector = mysql_connector if mysql_connector is not None else MySQLConnector()
        # mysql repository
        self.employee_repository = employee_repository if employee_repository is not None \
            else EmployeeRepository(mysql_connection=self.mysql_connector.get_connection())

        # exception
        self.exception = None

        if self.REDIS_ENABLED:
            # redis connection
            self.redis_connector = redis_connector if redis_connector is not None \
                else RedisConnector()
            # redis repository
            self.redis_employee_repository = None

        self.debug(self.DEBUG)

    def debug(self, flag: bool = False):
        """
        Ativa ou desativa o modo de depuração.

        Args:
            flag (bool, opcional): Define o estado do modo debug. Padrão é False.
        """
        self.DEBUG = flag
        self.employee_repository.debug = self.DEBUG
        if self.REDIS_ENABLED:
            self.redis_employee_repository.debug = self.DEBUG

    def list(self, request_formatted: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Lista os funcionários com base nos filtros fornecidos.

        Args:
            request_formatted (Dict[str, Any]): Filtros e parâmetros da consulta.

        Returns:
            List[Dict[str, Any]]: Lista de funcionários formatados para resposta da API.
        """
        self.logger.info('method: {} - request: {}'.format(
            get_function_name(), request_formatted))

        data: List[Dict[str, Any]] = []
        where = request_formatted['where']

        # exclude deleted
        where['deleted_at'] = None

        try:
            offset = request_formatted['offset']
            limit = request_formatted['limit']
            order_by = request_formatted['order_by']
            sort_by = request_formatted['sort_by']
            fields = request_formatted['fields']
            data = self.employee_repository.list(
                where=where, offset=offset, limit=limit, order_by=order_by,
                sort_by=sort_by, fields=fields)

            # convert to vo and prepare for api response
            if data:
                data = [EmployeeVO(**item).to_api_response() for item in data]

            # set exception if it happens
            if self.employee_repository.get_exception():
                raise DatabaseException(MessagesEnum.LIST_ERROR)

        except Exception as err:
            self.logger.error(f"Erro inesperado: {err}")
            self.exception = err

        return data

    def count(self, request: Dict[str, Any]) -> int:
        """
        Conta o número de funcionários com base nos filtros fornecidos.

        Args:
            request (Dict[str, Any]): Filtros e parâmetros da contagem.

        Returns:
            int: Quantidade total de funcionários encontrados.
        """
        self.logger.info('method: {} - request: {}'.format(get_function_name(), request))

        total = 0
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
            total = self.employee_repository.count(
                where=where, order_by=order_by, sort_by=sort_by)
        except Exception as err:
            self.logger.error(err)
            self.exception = DatabaseException(MessagesEnum.LIST_ERROR)

        return total

    def find(self, request: Dict[str, Any]) -> NoReturn:
        """
        Método não implementado para busca de funcionários.

        Args:
            request (Dict[str, Any]): Parâmetros da busca.

        Raises:
            ServiceException: Indica que o método não foi implementado.
        """
        self.logger.info('method: {} - request: {}'
                         .format(get_function_name(), request))
        raise ServiceException(MessagesEnum.METHOD_NOT_IMPLEMENTED_ERROR)

    def get(self, request: Dict[str, Any], employee_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtém um funcionário com base no ID fornecido.

        Args:
            request (Dict[str, Any]): Parâmetros da requisição.
            employee_id (str): Identificador único do funcionário.

        Returns:
            Optional[Dict[str, Any]]: Dados do funcionário ou None em caso de erro.

        Raises:
            DatabaseException: Caso ocorra um erro ao buscar os dados no banco.
        """
        self.logger.info('method: {} - request: {}'
                         .format(get_function_name(), request))

        self.logger.info('method: {} - id: {}'
                         .format(get_function_name(), employee_id))

        data = []
        where = request['where']

        try:
            fields = request['fields']
            value = employee_id
            data = self.employee_repository.get(
                value, key=self.employee_repository.PK, where=where, fields=fields
            )

            if self.DEBUG:
                self.logger.info('data: {}'.format(data))

            if isinstance(data, EmployeeVO):
                data = data.to_api_response()

            # set exception if it happens
            if self.employee_repository.get_exception():
                raise DatabaseException(MessagesEnum.FIND_ERROR)

        except Exception as err:
            self.logger.error(f"Erro inesperado: {err}")
            self.exception = err

        return data

    def create(self, request_formatted: dict) -> Optional[EmployeeVO]:
        """
        Cria um novo funcionário no sistema.

        Args:
            request_formatted (dict): Dados formatados da requisição.

        Returns:
            Optional[EmployeeVO]: Objeto EmployeeVO criado ou None em caso de erro.

        Raises:
            ValidationException: Caso os dados da requisição sejam inválidos.
            DatabaseException: Caso ocorra um erro ao salvar os dados no banco.
        """
        self.logger.info('method: {} - request: {}'.format(
            get_function_name(), request_formatted))

        data = request_formatted['where']
        if self.DEBUG:
            self.logger.info('method: {} - data: {}'.format(get_function_name(), data))

        try:
            if data == dict():
                raise ValidationException(MessagesEnum.REQUEST_ERROR)

            employee_vo = EmployeeVO(**data)
            created = self.employee_repository.create(employee_vo)

            if created:
                data = employee_vo
            else:
                data = None
                # set exception if it happens
                raise DatabaseException(MessagesEnum.CREATE_ERROR)

        except Exception as err:
            self.logger.error(f"Erro inesperado: {err}")
            self.exception = err

        return data

    def update(self, request_formatted: dict, employee_id: str) -> Optional[dict]:
        """
        Atualiza os dados de um funcionário existente.

        Args:
            request_formatted (dict): Dados formatados da requisição.
            employee_id (str): Identificador do funcionário.

        Returns:
            Optional[dict]: Dados atualizados do funcionário ou None em caso de erro.

        Raises:
            DatabaseException: Caso o funcionário não seja encontrado ou ocorra erro na atualização.
            ValidationException: Caso os dados fornecidos sejam inválidos.
        """
        self.logger.info(
            'method: {} - request: {}'.format(get_function_name(), request_formatted))

        original_employee = self.employee_repository.get(employee_id,
                                                         key=self.employee_repository.PK)
        if original_employee is None:
            raise DatabaseException(MessagesEnum.FIND_ERROR)

        data = request_formatted['where']
        if self.DEBUG:
            self.logger.info('method: {} - data: {}'.format(get_function_name(), data))

        # validate the request payload
        self.validate_data(data, original_employee)

        # update original employee with update data
        original_employee.update(data)
        data = original_employee

        try:
            if data == dict():
                raise ValidationException(MessagesEnum.REQUEST_ERROR)

            updated_at = helper.datetime_now_with_timezone()
            data.update({'updated_at': updated_at})

            employee_vo = data

            updated = self.employee_repository.update(employee_vo, id,
                                                      key=self.employee_repository.PK)

            if updated:
                data = employee_vo.to_api_response()
            else:
                data = None
                # set exception if it happens
                raise DatabaseException(MessagesEnum.UPDATE_ERROR)

        except Exception as err:
            self.logger.error(f"Erro inesperado: {err}")
            self.exception = err

        return data

    def delete(self, request: Dict[str, Any], employee_id: str) -> bool:
        """
       Realiza a exclusão lógica de um funcionário.

       Args:
           request (Dict[str, Any]): Dados formatados da requisição.
           employee_id (str): Identificador do funcionário.

       Returns:
           bool: True se a exclusão for bem-sucedida, False caso contrário.

       Raises:
           DatabaseException: Caso o funcionário não seja encontrado ou ocorra erro na exclusão.
       """
        self.logger.info('method: {} - request: {}'.format(get_function_name(), request))
        result = False

        original_employee = self.employee_repository.get(employee_id,
                                                         key=self.employee_repository.PK)
        if original_employee is None:
            raise DatabaseException(MessagesEnum.FIND_ERROR)

        try:
            updated = self.employee_repository.soft_delete(value=employee_id,
                                                           key=self.employee_repository.PK)

            if updated:
                result = True
            else:
                # set exception if it happens
                raise DatabaseException(MessagesEnum.SOFT_DELETE_ERROR)

        except Exception as err:
            self.logger.error(f"Erro inesperado: {err}")
            self.exception = err

        return result

    def validate_data(self, data: Dict[str, Any], original_employee: EmployeeVO) -> None:
        """
        Valida os campos do payload de atualização.

        Args:
           data (Dict[str, Any]): Dados enviados na requisição.
           original_employee (EmployeeVO): Dados originais do funcionário.

        Raises:
           ValidationException: Se algum campo não for permitido.
       """
        allowed_fields = list(original_employee.to_dict().keys())
        try:
            allowed_fields.remove(self.employee_repository.UUID_KEY)
            allowed_fields.remove(self.employee_repository.PK)
            allowed_fields.remove('updated_at')
            allowed_fields.remove('created_at')
            allowed_fields.remove('deleted_at')
        except Exception as err:
            self.logger.error(err)
        fields = list(data.keys())
        for field in fields:
            if field not in allowed_fields:
                exception = ValidationException(MessagesEnum.VALIDATION_ERROR)
                exception.params = [filter_xss_injection(data[field]), filter_xss_injection(field)]
                exception.set_message_params()
                raise exception
