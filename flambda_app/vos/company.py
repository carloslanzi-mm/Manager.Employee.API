import uuid as python_uuid
from datetime import datetime
from typing import Dict, Optional


class CompanyVO:
    """
    Value Object for Company
    """
    def __init__(self, name: str, id: Optional[int] = None, uuid: Optional[str] = None,
                 created_at: Optional[str] = None, updated_at: Optional[str] = None,
                 deleted_at: Optional[str] = None):

        self.id = id
        self.uuid = uuid or str(python_uuid.uuid4())
        self.name = name
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at
        self.deleted_at = deleted_at

    def __str__(self):
        """
        String representation of the CompanyVO instance.
        """
        return f"CompanyVO(id={self.id}, uuid={self.uuid}, name={self.name}, " \
               f"created_at={self.created_at}, updated_at={self.updated_at}, " \
               f"deleted_at={self.deleted_at})"

    def to_dict(self) -> Dict[str, str]:
        """
        Converts the CompanyVO to a dictionary.
        """
        return {
            'id': self.id,
            'uuid': self.uuid,
            'name': str(self.name) if self.name is not None else None,
            'created_at': str(self.created_at) if self.created_at is not None else None,
            'updated_at': str(self.updated_at) if self.updated_at is not None else None,
            'deleted_at': str(self.deleted_at) if self.deleted_at is not None else None
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
