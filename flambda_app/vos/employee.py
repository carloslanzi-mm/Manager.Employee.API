import uuid as python_uuid
from datetime import datetime
from typing import Dict, Optional, Any

from flambda_app.repositories.v1.mysql.company_repository import CompanyRepository


class EmployeeVO:
    """
    Value Object for Employee
    """
    id: Optional[int]
    uuid: str
    company_id: Optional[int]
    name: Optional[str]
    hourly_rate: Optional[float]
    is_admin: bool
    is_active: bool
    created_at: str
    updated_at: Optional[str]
    deleted_at: Optional[str]

    def __init__(
        self,
        id: Optional[int] = None,
        uuid: Optional[str] = None,
        company_id: Optional[int] = None,
        name: Optional[str] = None,
        hourly_rate: Optional[float] = None,
        is_admin: bool = False,
        is_active: bool = True,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        deleted_at: Optional[str] = None,
        **kwargs: Any
    ):
        self.id = id
        self.uuid = uuid or str(python_uuid.uuid4())
        self.company_id = company_id
        self.name = name
        self.hourly_rate = hourly_rate
        self.is_admin = is_admin
        self.is_active = is_active
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at
        self.deleted_at = deleted_at

        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __str__(self):
        """
        String representation of the EmployeeVO instance.
        """
        return f"EmployeeVO(id={self.id}, uuid={self.uuid}, company_id={self.company_id}, name={self.name}, " \
               f"hourly_rate={self.hourly_rate}, is_admin={self.is_admin}, is_active={self.is_active}, " \
               f"created_at={self.created_at}, updated_at={self.updated_at}, deleted_at={self.deleted_at})"

    def to_dict(self) -> Dict[str, Optional[str]]:
        """
        Converts the EmployeeVO to a dictionary.
        """
        return {
            'id': self.id,
            'uuid': self.uuid,
            'company_id': self.company_id,
            'name': self.name,
            'hourly_rate': self.hourly_rate,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'deleted_at': self.deleted_at
        }

    def update(self, data: dict):
        """
        Update the EmployeeVO instance with the provided data.
        """
        if 'company_id' in data:
            self.company_id = data['company_id']
        if 'name' in data:
            self.name = data['name']
        if 'hourly_rate' in data:
            self.hourly_rate = data['hourly_rate']
        if 'is_admin' in data:
            self.is_admin = data['is_admin']
        if 'is_active' in data:
            self.is_active = data['is_active']
        if 'created_at' in data:
            self.created_at = data['created_at']
        if 'updated_at' in data:
            self.updated_at = data['updated_at']
        if 'deleted_at' in data:
            self.deleted_at = data['deleted_at']

    def get_company_name(self) -> Optional[str]:
        """Busca o nome da empresa usando CompanyService se não estiver no dicionário."""
        if not self.company_id:
            return None

        company_repository = CompanyRepository()
        company_data = company_repository.get(value=self.company_id, key='id', fields=['name'])
        return company_data.name if company_data else None

    def to_api_response(self) -> Dict[str, str]:
        """
        Convert EmployeeVO to a response format.
        """
        return {
            "id": self.id,
            "uuid": self.uuid,
            "company_id": self.company_id,
            "company_name": self.get_company_name(),
            "name": self.name,
            "hourly_rate": self.hourly_rate,
            "is_admin": self.is_admin,
            "is_active": self.is_active
        }
