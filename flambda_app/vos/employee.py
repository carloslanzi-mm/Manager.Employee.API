import uuid
from datetime import datetime

from flambda_app.repositories.v1.mysql.company_repository import CompanyRepository


class EmployeeVO:
    """
    Value Object for Employee
    """

    def __init__(self, data: dict = None, default_values=True):
        """
        Initialize the EmployeeVO object with the given data or set default values.
        """
        self.id = data.get('id') if data and "id" in data else None
        self.uuid = data.get('uuid') if data and "uuid" in data \
            else str(uuid.uuid4()) if default_values else None
        self.company_id = data.get('company_id') if data and "company_id" in data else None
        self.name = data.get('name') if data and "name" in data else None
        self.hourly_rate = data.get('hourly_rate') if data and "hourly_rate" in data else None
        self.is_admin = data.get('is_admin') if data and "is_admin" in data else False
        self.is_active = data.get('is_active') if data and "is_active" in data else True
        self.created_at = data.get('created_at') if data and 'created_at' in data \
            else datetime.now().isoformat() if default_values else None
        self.updated_at = data.get('updated_at') if data and 'updated_at' in data else None
        self.deleted_at = data.get('deleted_at') if data and 'deleted_at' in data else None

    def __str__(self):
        """
        String representation of the EmployeeVO instance.
        """
        return f"EmployeeVO(id={self.id}, uuid={self.uuid}, company_id={self.company_id}, name={self.name}, " \
               f"hourly_rate={self.hourly_rate}, is_admin={self.is_admin}, is_active={self.is_active}, " \
               f"created_at={self.created_at}, updated_at={self.updated_at}, deleted_at={self.deleted_at})"

    def to_dict(self):
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

    def get_company_name(self):
        """Busca o nome da empresa usando CompanyService se não estiver no dicionário."""
        if not self.company_id:
            return None

        company_repository = CompanyRepository()
        company_data = company_repository.get(value=self.company_id, key='id', fields=['name'])
        return company_data.name if company_data else None

    def to_api_response(self):
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
            else str(uuid.uuid4()) if default_values else None
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