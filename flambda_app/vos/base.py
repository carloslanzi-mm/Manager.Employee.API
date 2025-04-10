from datetime import datetime
from typing import Optional, Dict, Any, List, Set

from flambda_app.enums.messages import MessagesEnum
from flambda_app.exceptions import ValidationException


class Base:
    update_allowed_fields: List[str] = []
    required_fields: List[str] = []
    custom_validators = {}
    filter_allowed_fields: List[str] = []
    always_allowed_query_params: Set[str] = {'sort_by', 'order_by', 'limit', 'offset'}

    def update(self, data: Dict[str, Any]) -> None:
        """
        Atualiza os campos permitidos com os dados fornecidos, validando obrigatórios.

        :param data: Dicionário com dados a serem atualizados.
        :raises ValidationException: Caso um campo obrigatório esteja ausente ou inválido.
        """
        for field in self.update_allowed_fields:
            if field in data:
                value = data[field]

                # Validação para campos obrigatórios no update
                if field in self.required_fields and (value is None or (isinstance(value, str)
                                                                        and not value.strip())):
                    msg = f"campo '{field}' é obrigatório e não pode ser vazio ou nulo."
                    raise ValidationException(
                        MessagesEnum.VALIDATION_ERROR,
                        errors={
                            "field": field,
                            "message": msg,
                            "value": value
                        }
                    )

                setattr(self, field, value)

    def validate_required_fields(self) -> Optional[str]:
        """
        Verifica se os campos obrigatórios estão preenchidos e válidos.

        :return: Nome do campo com erro ou `None` se tudo estiver válido.
        """
        for field in self.required_fields:
            value = getattr(self, field, None)
            if value is None or (isinstance(value, str) and not value.strip()):
                return f"O campo '{field}' é obrigatório."

        for field, validator in getattr(self, "custom_validators", {}).items():
            value = getattr(self, field, None)
            if not validator(value):
                return field

        return None

    def filter_allowed_fields_data(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filtra o dicionário de filtros, mantendo apenas os campos permitidos.

        :param filters: Dicionário original de filtros.
        :return: Novo dicionário com apenas os filtros permitidos.
        """
        allowed = getattr(self, "filter_allowed_fields", [])
        always_allowed = getattr(self, "always_allowed_query_params", set())
        return {
            key: value
            for key, value in filters.items()
            if key.split("__")[0] in allowed or key in always_allowed
        }

    def is_only_sorting_or_pagination(self, query_args: dict) -> bool:
        """
        Verifica se os parâmetros da query contêm apenas paginação ou ordenação.

        :param query_args: Parâmetros da query string.
        :return: True se todos os parâmetros forem permitidos por default.
        """
        return all(k in self.always_allowed_query_params for k in query_args)


class BaseDocumentFile(Base):
    update_allowed_fields = [
        "name", "type_id", "url",
        "updated_at", "deleted_at"
    ]

    id: Optional[int]
    company_id: Optional[int]
    name: Optional[str]
    type_id: Optional[int]
    url: Optional[str]
    created_at: str
    updated_at: Optional[str]
    deleted_at: Optional[str]

    def __init__(self,
                 id: Optional[int] = None,
                 company_id: Optional[int] = None,
                 name: Optional[str] = None,
                 type_id: Optional[int] = None,
                 url: Optional[str] = None,
                 created_at: Optional[str] = None,
                 updated_at: Optional[str] = None,
                 deleted_at: Optional[str] = None,
                 **kwargs: Any
                 ):
        """
        Inicializa uma instância de BaseDocumentFile com os campos fornecidos.

        :param kwargs: Campos adicionais compatíveis com atributos existentes.
        """

        self.id = id
        self.company_id = company_id
        self.name = name
        self.type_id = type_id
        self.url = url
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at
        self.deleted_at = deleted_at

        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def to_dict(self) -> Dict[str, Optional[str]]:
        """
        Converte os dados da instância para um dicionário completo.

        :return: Dicionário com todos os campos principais.
        """
        return {
            "id": self.id,
            "company_id": self.company_id,
            "name": self.name,
            "type_id": self.type_id,
            "url": self.url,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "deleted_at": self.deleted_at
        }

    def get_type_name(self) -> Optional[str]:
        """
        Busca o nome do tipo relacionado à instância via repositório.

        :return: Nome do tipo se encontrado, ou None.
        """
        if not self.type_id:
            return None

        from .type import Type
        from flambda_app.repositories.v1.mysql.files_document_repository import \
            FilesDocumentRepository

        report_repository = FilesDocumentRepository()
        data = report_repository.get_entity('type',
                                            vo_class=Type,
                                            value=self.type_id,
                                            key='id',
                                            fields=['name'])

        return data.name if data else None

    def to_api_response(self) -> Dict[str, Optional[str]]:
        """
        Converte os dados da instância para um dicionário com estrutura para API.

        :return: Dicionário formatado para resposta de API.
        """
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "type": {
                "id": self.type_id,
                "name": self.get_type_name(),
            }
        }
