import uuid as python_uuid
from datetime import datetime
from typing import Dict, Optional, Any

from flambda_app.repositories.v1.mysql.company_repository import CompanyRepository
from flambda_app.vos.base import Base


class EmployeeVO(Base):
    """
    Object for Employee
    """

    update_allowed_fields = [
        "company_id",
        "name",
        "hourly_rate",
        "is_admin",
        "is_active",
        "created_at",
        "updated_at",
        "deleted_at",
    ]

    employee_id: Optional[int]
    uuid: str
    company_id: Optional[int]
    name: Optional[str]
    hourly_rate: Optional[float]
    is_admin: bool
    is_active: bool
    created_at: str
    updated_at: Optional[str]
    deleted_at: Optional[str]

    def __init__(self,
                 employee_id: Optional[int] = None,
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

        self.id = employee_id
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
        return f"EmployeeVO(id={self.id}, uuid={self.uuid}, company_id={self.company_id}, " \
               f"name={self.name}, hourly_rate={self.hourly_rate}, is_admin={self.is_admin}, " \
               f"is_active={self.is_active}, created_at={self.created_at}, " \
               f"updated_at={self.updated_at}, deleted_at={self.deleted_at})"

    def to_dict(self) -> Dict[str, Optional[str]]:
        """
        Converts the EmployeeVO to a dictionary.
        """
        return {
            "id": self.id,
            "uuid": self.uuid,
            "company_id": self.company_id,
            "name": self.name,
            "hourly_rate": self.hourly_rate,
            "is_admin": self.is_admin,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "deleted_at": self.deleted_at
        }

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


class EmployeeTurnstileInputVO:
    """
    Value Object for Employee Turnstile Input
    """

    def __init__(self, data: dict = None, default_values=True):
        """
        Initialize the EmployeeVO object with the given data or set default values.
        """
        self.uuid = (
            data.get("uuid")
            if data and "uuid" in data
            else str(python_uuid.uuid4()) if default_values else None
        )
        self.name = data.get("name") if data and "name" in data else None
        self.is_active = data.get("is_active") if data and "is_active" in data else True

    def to_dict(self):
        """
        Converts the EmployeeVO to a dictionary.
        """
        return {
            "uuid": self.uuid,
            "name": self.name,
            "is_active": self.is_active,
        }
