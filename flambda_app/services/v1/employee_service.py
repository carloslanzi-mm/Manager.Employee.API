import copy
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
# from flambda_app.repositories.v1.redis.employee_repository import \
#     EmployeeRepository as RedisEmployeeRepository
from flambda_app.vos.employee import EmployeeVO


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

    def list(self, request_formatted: Dict[str, Any]) -> List[Dict[str, Any]]:
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
            self.logger.error(err)
            self.exception = err

        return data

    def count(self, request: Dict[str, Any]) -> int:
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
        self.logger.info('method: {} - request: {}'
                         .format(get_function_name(), request))
        raise ServiceException(MessagesEnum.METHOD_NOT_IMPLEMENTED_ERROR)

    def get(self, request: Dict[str, Any], id: str) -> Optional[Dict[str, Any]]:
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

    def create(self, request_formatted: dict) -> Optional[EmployeeVO]:
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
            self.logger.error(err)
            self.exception = err

        return data

    def update(self, request_formatted: dict, id: str) -> Optional[dict]:
        self.logger.info(
            'method: {} - request: {}'.format(get_function_name(), request_formatted))

        original_employee = self.employee_repository.get(id, key=self.employee_repository.PK)
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
            self.logger.error(err)
            self.exception = err

        return data

    def delete(self, request: Dict[str, Any], id: str) -> bool:
        self.logger.info('method: {} - request: {}'.format(get_function_name(), request))
        result = False

        original_employee = self.employee_repository.get(id, key=self.employee_repository.PK)
        if original_employee is None:
            raise DatabaseException(MessagesEnum.FIND_ERROR)

        try:
            updated = self.employee_repository.soft_delete(value=id,
                                                           key=self.employee_repository.PK)

            if updated:
                result = True
            else:
                # set exception if it happens
                raise DatabaseException(MessagesEnum.SOFT_DELETE_ERROR)

        except Exception as err:
            self.logger.error(err)
            self.exception = err

        return result

    def validate_data(self, data: Dict[str, Any], original_employee: EmployeeVO) -> None:
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
