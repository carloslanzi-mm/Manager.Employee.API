from flambda_app import helper
from flambda_app.database.mysql import MySQLConnector
from flambda_app.database.redis import RedisConnector
from flambda_app.enums.messages import MessagesEnum
from flambda_app.exceptions import DatabaseException, ValidationException, ServiceException
from flambda_app.filter_helper import filter_xss_injection
from flambda_app.helper import get_function_name
from flambda_app.logging import get_logger
from flambda_app.repositories.v1.mysql.company_repository import CompanyRepository
# from flambda_app.repositories.v1.redis.company_repository import \
#     CompanyRepository as RedisCompanyRepository
from flambda_app.vos.company import CompanyVO


class CompanyService:
    DEBUG = False
    REDIS_ENABLED = False

    def __init__(self, logger=None, mysql_connector=None, redis_connector=None,
                 company_repository=None,
                 redis_company_repository=None):
        # logger
        self.logger = logger if logger is None else get_logger()
        # database connection
        self.mysql_connector = mysql_connector if mysql_connector is not None else MySQLConnector()
        # todo passar apenas connector
        # mysql repository
        self.company_repository = company_repository if company_repository is not None \
            else CompanyRepository(mysql_connection=self.mysql_connector.get_connection())

        # exception
        self.exception = None

        if self.REDIS_ENABLED:
            # redis connection
            self.redis_connector = redis_connector if redis_connector is not None else RedisConnector()
            # todo passar apenas connector
            # redis repository
            self.redis_company_repository = None  # redis_company_repository if
            # redis_company_repository is not None \ else RedisCompanyRepository(
            # redis_connection=self.redis_connector.get_connection())

        self.debug(self.DEBUG)

    def debug(self, flag: bool = False):
        self.DEBUG = flag
        self.company_repository.debug = self.DEBUG
        if self.REDIS_ENABLED:
            self.redis_company_repository.debug = self.DEBUG

    def list(self, request_formatted: dict) -> CompanyVO:
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
                vo_data = []
                for item in data:
                    vo_data.append(CompanyVO(**item).to_api_response())
                data = vo_data

            # set exception if it happens
            if self.company_repository.get_exception():
                raise DatabaseException(MessagesEnum.LIST_ERROR)

        except Exception as err:
            self.logger.error(err)
            self.exception = err

        return data

    def count(self, request: dict):
        self.logger.info('method: {} - request: {}'
                         .format(get_function_name(), request))

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
            total = self.company_repository.count(
                where=where, order_by=order_by, sort_by=sort_by)
        except Exception as err:
            self.logger.error(err)
            self.exception = DatabaseException(MessagesEnum.LIST_ERROR)

        return total

    def find(self, request: dict):
        self.logger.info('method: {} - request: {}'
                         .format(get_function_name(), request))
        raise ServiceException(MessagesEnum.METHOD_NOT_IMPLEMENTED_ERROR)

    def get(self, request_formatted: dict, id: int) -> CompanyVO:
        self.logger.info('method: {} - request: {}'
                         .format(get_function_name(), request_formatted))

        self.logger.info('method: {} - uuid: {}'
                         .format(get_function_name(), id))

        data = []
        where = request_formatted['where']

        try:
            fields = request_formatted['fields']
            value = id
            data = self.company_repository.get(
                value, key=self.company_repository.PK, where=where, fields=fields
            )

            if self.DEBUG:
                self.logger.info('data: {}'.format(data))

            # convert to vo and prepare for api response
            if data and isinstance(data, dict):
                data = CompanyVO(**data).to_api_response()

            # set exception if it happens
            if self.company_repository.get_exception():
                raise DatabaseException(MessagesEnum.FIND_ERROR)

        except Exception as err:
            self.logger.error(err)
            self.exception = err

        return data

    def create(self, request_formatted: dict) -> CompanyVO:
        self.logger.info('method: {} - request: {}'.format(
            get_function_name(), request_formatted))

        data = request_formatted['where']
        if self.DEBUG:
            self.logger.info('method: {} - data: {}'.format(get_function_name(), data))

        try:

            if data == dict():
                raise ValidationException(MessagesEnum.REQUEST_ERROR)

            company_vo = CompanyVO(**data)
            created = self.company_repository.create(company_vo)

            if created:
                data = company_vo

            else:
                data = None
                # set exception if it happens
                raise DatabaseException(MessagesEnum.CREATE_ERROR)

        except Exception as err:
            self.logger.error(err)
            self.exception = err

        return data

    def update(self, request_formatted: dict, uuid) -> CompanyVO:

        self.logger.info('method: {} - request: {}'.format(
            get_function_name(), request_formatted))

        original_company = self.company_repository.get(uuid, key=self.company_repository.PK)
        if original_company is None:
            raise DatabaseException(MessagesEnum.FIND_ERROR)

        data = request_formatted['where']
        if self.DEBUG:
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

        except Exception as err:
            self.logger.error(err)
            self.exception = err

        return data

    def delete(self, request_formatted: dict, uuid) -> CompanyVO:

        self.logger.info('method: {} - request: {}'.format(
            get_function_name(), request_formatted))
        result = False

        original_company = self.company_repository.get(uuid, key=self.company_repository.PK)
        if original_company is None:
            raise DatabaseException(MessagesEnum.FIND_ERROR)

        try:

            updated = self.company_repository.soft_delete(value=uuid,
                                                          key=self.company_repository.PK)

            if updated:
                result = True
            else:
                # set exception if it happens
                raise DatabaseException(MessagesEnum.SOFT_DELETE_ERROR)

        except Exception as err:
            self.logger.error(err)
            self.exception = err

        return result

    def validate_data(self, data, original_company):
        allowed_fields = list(original_company.to_dict().keys())
        try:
            allowed_fields.remove(self.company_repository.UUID_KEY)
            allowed_fields.remove(self.company_repository.PK)
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
