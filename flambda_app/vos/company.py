import uuid as python_uuid
from datetime import datetime
from typing import Dict, Optional, Any


class CompanyVO:
    """
    Value Object for Company
    """
    id: Optional[int]
    uuid: str
    name: Optional[str]
    created_at: str
    updated_at: Optional[str]
    deleted_at: Optional[str]

    def __init__(
        self,
        id: Optional[int] = None,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        deleted_at: Optional[str] = None,
        **kwargs: Any
    ):

        self.id = id
        self.uuid = uuid or str(python_uuid.uuid4())
        self.name = name
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at
        self.deleted_at = deleted_at

        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __str__(self):
        """
        String representation of the CompanyVO instance.
        """
        return f"CompanyVO(id={self.id}, uuid={self.uuid}, name={self.name}, " \
               f"created_at={self.created_at}, updated_at={self.updated_at}, " \
               f"deleted_at={self.deleted_at})"

    def to_dict(self) -> Dict[str, Optional[str]]:
        """
        Converts the CompanyVO to a dictionary.
        """
        return {
            'id': self.id,
            'uuid': self.uuid,
            'name': self.name,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'deleted_at': self.deleted_at
        }

    def update(self, data: dict):
        """
        Update the CompanyVO instance with the provided data.
        """
        if 'name' in data:
            self.name = data['name']
        if 'created_at' in data:
            self.created_at = data['created_at']
        if 'updated_at' in data:
            self.updated_at = data['updated_at']
        if 'deleted_at' in data:
            self.deleted_at = data['deleted_at']

    def to_api_response(self) -> Dict[str, str]:
        return {
            "id": self.id,
            "uuid": self.uuid,
            "name": self.name
        }
