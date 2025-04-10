"""
Módulo responsável por gerenciar operações relacionadas a empresas.
"""

from typing import Union, List, Optional, Any, Dict

from flambda_app.config import get_config
from flambda_app.enums.messages import MessagesEnum
from flambda_app.exceptions import ValidationException
from flambda_app.logging import get_logger
from flambda_app.services.v1.company_service import CompanyService
from flambda_app.http_resources.request import ApiRequest
from flambda_app.vos.company import CompanyVO
from flambda_app.vos.address import Address


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

    def _validate_required_fields(self, vo_instance: Any, data_dict: Dict[str, Any]) -> None:
        """
        Valida os campos obrigatórios de uma instância de Value Object (VO).

        Chama o método `validate_required_fields()` da instância e,
        caso algum campo obrigatório esteja ausente ou inválido,
        dispara uma `ValidationException`.

        :param vo_instance: Instância de um VO que herda da Base metodo `validate_required_fields`.
        :param data_dict: Dicionário original com os dados recebidos (ex: payload da requisição).
        :raises ValidationException: Se algum campo obrigatório estiver ausente ou inválido.
        """
        missing_field = vo_instance.validate_required_fields()
        if missing_field:
            self.exception = ValidationException(
                MessagesEnum.VALIDATION_ERROR,
                errors={'field': missing_field, 'value': data_dict.get(missing_field)}
            )
            raise self.exception

    def debug(self, flag: bool = False):
        """
       Define o modo de depuração.

       :param flag: Se True, ativa o modo de depuração.
       """
        self.debug_mode = flag
        self.company_service.debug(self.debug_mode)

    def list(self, request: ApiRequest) -> List[Union[CompanyVO, dict]]:
        """
        Lista empresas com base nos filtros fornecidos na requisição.

        Aplica os filtros permitidos definidos em `CompanyVO.filter_allowed_fields` e
        verifica se a requisição contém apenas parâmetros de paginação/ordenação.

        :param request: Objeto da requisição contendo dados do query string e do body.
        :return: Lista de instâncias de `CompanyVO` ou dicionários representando empresas.
        :raises ValidationException ou outra exceção propagada pela `company_service`, se houver erro.
        """

        request_data = request.to_dict()

        instance = CompanyVO()
        allowed_filters = instance.filter_allowed_fields_data(
            request_data.get('where', {})
        )
        request_data['where'] = allowed_filters

        # Evita listagem se a query possui parâmetros não permitidos
        if request.query_string_args and not allowed_filters:
            if not instance.is_only_sorting_or_pagination(request.query_string_args):
                return []

        data = self.company_service.list(request_data)
        if (data is None or len(data) == 0) and self.company_service.exception:
            self.exception = self.company_service.exception
            raise self.exception
        return data or []

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

        files = [file.to_api_response() for file in data.get('files', [])]
        documents = [document.to_api_response() for document in data.get('documents', [])]

        return {"company": data['company'].to_api_response(),
                "address": data['address'].to_api_response(),
                "documents": documents,
                "files": files}

    def create(self, request: ApiRequest) -> Optional[Dict[str, Any]]:
        """
        Cria uma nova empresa e seu endereço com base nos dados fornecidos na requisição.

        Realiza a validação dos campos obrigatórios para `CompanyVO` e `Address`,
        antes de delegar a criação à camada de serviço.

        :param request: Objeto da requisição contendo os dados para criação.
        :return: Dicionário com os dados da empresa e do endereço criados, ou None.
        :raises ValidationException: Caso algum campo obrigatório não seja informado.
        """

        data = request.to_dict()
        where_data = data.get("where", {})
        company_data = where_data.get("company", {})
        address_data = where_data.get("address", {})

        company_vo = CompanyVO(**company_data)
        self._validate_required_fields(company_vo, company_data)

        address_vo = Address(**address_data)
        self._validate_required_fields(address_vo, address_data)

        company_obj, address_obj = self.company_service.create(request.to_dict())

        if self.company_service.exception:
            self.exception = self.company_service.exception
            raise self.exception

        return {
            "company": company_obj.to_api_response(),
            "address": address_obj.to_api_response()
        }

    def update(self, request: ApiRequest, company_id: str):
        """
        Atualiza uma empresa com base no ID.

        :param request: Objeto de requisição.
        :param company_id: ID da empresa.
        :return: Dados da empresa atualizada ou None.
        """
        company, address = self.company_service.update(request.to_dict(), company_id)
        if (company is None or address is None) and self.company_service.exception:
            self.exception = self.company_service.exception
            raise self.exception

        return {
            "company": company.to_api_response(),
            "address": address.to_api_response()
        }

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
