from flambda_app.config import get_config
from flambda_app.logging import get_logger
from flambda_app.services.v1.company_service import CompanyService
from flambda_app.http_resources.request import ApiRequest
from flambda_app.vos.company import CompanyVO


class CompanyManager:
    def __init__(self, logger=None, config=None, company_service=None):
        self.logger = logger if logger is not None else get_logger()
        # configurations
        self.config = config if config is not None else get_config()
        # service
        self.company_service = company_service if company_service is not None else CompanyService(
            self.logger)

        # exception
        self.exception = None

        # debug
        self.DEBUG = None

    def debug(self, flag: bool = False):
        self.DEBUG = flag
        self.company_service.debug(self.DEBUG)

    def list(self, request: dict):
        data = self.company_service.list(request)
        if (data is None or len(data) == 0) and self.company_service.exception:
            self.exception = self.company_service.exception
            raise self.exception
        return data

    def count(self, request: dict):
        total = self.company_service.count(request)
        if self.company_service.exception:
            self.exception = self.company_service.exception
            raise self.exception
        return total

    def get(self, request: dict, id):
        data = self.company_service.get(request, id)
        if (data is None) and self.company_service.exception:
            self.exception = self.company_service.exception
            raise self.exception
        return data

    def create(self, request: ApiRequest) -> CompanyVO:
        data = self.company_service.create(request.to_dict())
        if (data is None) and self.company_service.exception:
            self.exception = self.company_service.exception
            raise self.exception
        return data

    def update(self, request: ApiRequest, uuid) -> CompanyVO:
        data = self.company_service.update(request.to_dict(), uuid)
        if (data is None) and self.company_service.exception:
            self.exception = self.company_service.exception
            raise self.exception
        return data

    def delete(self, request: dict, uuid):
        result = self.company_service.delete(request, uuid)
        if (result is None) and self.company_service.exception:
            self.exception = self.company_service.exception
            raise self.exception
        return result
