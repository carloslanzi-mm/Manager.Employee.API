import copy
import os

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from flambda_app import helper
from flambda_app.database.mysql import MySQLConnector
from flambda_app.database.redis import RedisConnector
from flambda_app.enums.messages import MessagesEnum
from flambda_app.exceptions import DatabaseException, ServiceException, ValidationException
from flambda_app.filter_helper import filter_xss_injection
from flambda_app.helper import get_function_name
from flambda_app.logging import get_logger
from flambda_app.repositories.v1.mysql.employee_respository import EmployeeRepository
# from flambda_app.repositories.v1.redis.employee_repository import \
#     EmployeeRepository as RedisEmployeeRepository
from flambda_app.vos.employee import EmployeeTurnstileInputVO, EmployeeVO


class EmployeeService:
    DEBUG = False
    REDIS_ENABLED = False

    def __init__(self, logger=None, mysql_connector=None, redis_connector=None,
                 employee_repository=None,
                 redis_employee_repository=None):
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
            self.redis_connector = redis_connector if redis_connector is not None else RedisConnector()
            # redis repository
            self.redis_employee_repository = None  # redis_employee_repository if
            # redis_employee_repository is not None \ else RedisEmployeeRepository(
            # redis_connection=self.redis_connector.get_connection())

        self.debug(self.DEBUG)

    def debug(self, flag: bool = False):
        self.DEBUG = flag
        self.employee_repository.debug = self.DEBUG
        if self.REDIS_ENABLED:
            self.redis_employee_repository.debug = self.DEBUG

    def list(self, request: dict):
        self.logger.info('method: {} - request: {}'.format(get_function_name(), request))

        data = []
        where = request['where']

        # exclude deleted
        where['deleted_at'] = None

        try:
            offset = request['offset']
            limit = request['limit']
            order_by = request['order_by']
            sort_by = request['sort_by']
            fields = request['fields']
            data = self.employee_repository.list(
                where=where, offset=offset, limit=limit, order_by=order_by,
                sort_by=sort_by, fields=fields)

            # convert to vo and prepare for api response
            if data:
                vo_data = []
                for item in data:
                    vo_data.append(EmployeeVO(item, default_values=False).to_api_response())
                data = vo_data

            # set exception if it happens
            if self.employee_repository.get_exception():
                raise DatabaseException(MessagesEnum.LIST_ERROR)

        except Exception as err:
            self.logger.error(err)
            self.exception = err

        return data

    def count(self, request: dict):
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

    def find(self, request: dict):
        self.logger.info('method: {} - request: {}'
                         .format(get_function_name(), request))
        raise ServiceException(MessagesEnum.METHOD_NOT_IMPLEMENTED_ERROR)

    def get(self, request: dict, id):
        self.logger.info('method: {} - request: {}'
                         .format(get_function_name(), request))

        self.logger.info('method: {} - uuid: {}'
                         .format(get_function_name(), id))

        data = []
        where = request['where']

        try:
            fields = request['fields']
            value = id
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
            self.logger.error(err)
            self.exception = err

        return data

    def create(self, request: dict):
        self.logger.info('method: {} - request: {}'.format(get_function_name(), request))

        data = request['where']
        if self.DEBUG:
            self.logger.info('method: {} - data: {}'.format(get_function_name(), data))

        try:
            if data == dict():
                raise ValidationException(MessagesEnum.REQUEST_ERROR)

            employee_vo = EmployeeVO(data)
            created = self.employee_repository.create(employee_vo)

            if created:
                employee_turnstile_input_vo = EmployeeTurnstileInputVO(
                    employee_vo.to_dict()
                )
                self.employee_turnstile_call(employee_turnstile_input_vo, 'POST')
                # convert to vo and prepare for api response
                data = employee_vo.to_api_response()
            else:
                data = None
                # set exception if it happens
                raise DatabaseException(MessagesEnum.CREATE_ERROR)

        except Exception as err:
            self.logger.error(err)
            self.exception = err

        return data

    def update(self, request: dict, id):
        self.logger.info('method: {} - request: {}'.format(get_function_name(), request))

        original_employee = self.employee_repository.get(id, key=self.employee_repository.PK)
        if original_employee is None:
            raise DatabaseException(MessagesEnum.FIND_ERROR)

        data = request['where']
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
                employee_turnstile_input_vo = EmployeeTurnstileInputVO(
                    employee_vo.to_dict()
                )
                self.employee_turnstile_call(employee_turnstile_input_vo, 'PATCH')
                # convert to vo and prepare for api response
                data = employee_vo.to_api_response()
            else:
                data = None
                # set exception if it happens
                raise DatabaseException(MessagesEnum.UPDATE_ERROR)

        except Exception as err:
            self.logger.error(err)
            self.exception = err

        return data

    def delete(self, request: dict, id):
        self.logger.info('method: {} - request: {}'.format(get_function_name(), request))
        result = False

        original_employee = self.employee_repository.get(id,
                                                         key=self.employee_repository.PK)
        if original_employee is None:
            raise DatabaseException(MessagesEnum.FIND_ERROR)

        try:
            updated = self.employee_repository.soft_delete(value=id,
                                                           key=self.employee_repository.PK)

            if updated:
                result = True
                employee_turnstile_input_vo = EmployeeTurnstileInputVO(
                    original_employee.to_dict()
                )
                self.employee_turnstile_call(employee_turnstile_input_vo, 'DELETE')
            else:
                # set exception if it happens
                raise DatabaseException(MessagesEnum.SOFT_DELETE_ERROR)

        except Exception as err:
            self.logger.error(err)
            self.exception = err

        return result

    def validate_data(self, data, original_employee):
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
            if not field in allowed_fields:
                exception = ValidationException(MessagesEnum.VALIDATION_ERROR)
                exception.params = [filter_xss_injection(data[field]), filter_xss_injection(field)]
                exception.set_message_params()
                raise exception

    def employee_turnstile_call(self, employee_turnstile_input_vo: EmployeeTurnstileInputVO, http_method: str = 'POST'):
        try:
            session = requests.Session()
            retry_strategy = Retry(total=3, backoff_factor=0.5)
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)

            turnstile_data = employee_turnstile_input_vo.to_dict()
            turnstile_url = os.getenv("TURNSTILE_API_URL", "http://localhost:5000")
            base_url = f"{turnstile_url}/v1/turnstile"

            # Adiciona o UUID para métodos que precisam dele
            if http_method.upper() in ['DELETE', 'PUT', 'PATCH']:
                uuid = turnstile_data.get('uuid')
                base_url = f"{base_url}/{uuid}"

            # Dicionário com os métodos HTTP disponíveis
            http_methods = {
                'POST': lambda: session.post(
                    base_url,
                    json=turnstile_data,
                    headers={"Content-Type": "application/json"},
                    timeout=5
                ),
                'DELETE': lambda: session.delete(
                    base_url,
                    headers={"Content-Type": "application/json"},
                    timeout=5
                ),
                'PUT': lambda: session.put(
                    base_url,
                    json=turnstile_data,
                    headers={"Content-Type": "application/json"},
                    timeout=5
                ),
                'PATCH': lambda: session.patch(
                    base_url,
                    json={
                        "name": turnstile_data.get("name"),
                        "is_active": turnstile_data.get("is_active")
                    },
                    headers={"Content-Type": "application/json"},
                    timeout=5
                )
            }

            method = http_method.upper()
            if method not in http_methods:
                raise ValueError(f"Método HTTP não suportado: {http_method}")

            turnstile_response = http_methods[method]()

            if turnstile_response.status_code != 200:
                self.logger.error(
                    f"Erro ao {http_method.lower()} registro na catraca: {turnstile_response.text}"
                )

        except Exception as turnstile_error:
            self.logger.error(
                f"Erro ao chamar endpoint da catraca ({http_method}): {str(turnstile_error)}"
            )
