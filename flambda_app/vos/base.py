from datetime import datetime
from typing import Optional, Dict, Any


class Base:
    update_allowed_fields = []

    def update(self, data: dict):
        """
        Atualiza a instância com os dados fornecidos.

        Args:
            data (dict): Dados para atualização.
        """
        for field in self.update_allowed_fields:
            if field in data:
                setattr(self, field, data[field])


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
        """Busca o nome da empresa usando CompanyService se não estiver no dicionário."""
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
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "type": {
                "id": self.type_id,
                "name": self.get_type_name(),
            }
        }
