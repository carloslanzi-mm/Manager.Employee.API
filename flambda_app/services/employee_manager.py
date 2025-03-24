from flambda_app.config import get_config
from flambda_app.http_resources.response import ApiResponse
from flambda_app.logging import get_logger
from flambda_app.services.v1.employee_service import EmployeeService
from flambda_app.vos.employee import EmployeeVO


class EmployeeManager:
    def __init__(self, logger=None, config=None, employee_service=None):
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
        self.DEBUG = flag
        self.employee_service.debug(self.DEBUG)

    def list(self, request: dict):
        data = self.employee_service.list(request)
        if (data is None or len(data) == 0) and self.employee_service.exception:
            self.exception = self.employee_service.exception
            raise self.exception
        return data

    def count(self, request: dict):
        total = self.employee_service.count(request)
        if self.employee_service.exception:
            self.exception = self.employee_service.exception
            raise self.exception
        return total

    def get(self, request: dict, id):
        data = self.employee_service.get(request, id)
        if (data is None) and self.employee_service.exception:
            self.exception = self.employee_service.exception
            raise self.exception
        return data

    def create(self, request: ApiResponse) -> EmployeeVO:
        data = self.employee_service.create(request.to_dict())
        if (data is None) and self.employee_service.exception:
            self.exception = self.employee_service.exception
            raise self.exception
        return data

    def update(self, request: ApiResponse, id: int):
        data = self.employee_service.update(request.to_dict(), id)
        if (data is None) and self.employee_service.exception:
            self.exception = self.employee_service.exception
            raise self.exception
        return data

    def delete(self, request: dict, id):
        result = self.employee_service.delete(request, id)
        if (result is None) and self.employee_service.exception:
            self.exception = self.employee_service.exception
            raise self.exception
        return result
