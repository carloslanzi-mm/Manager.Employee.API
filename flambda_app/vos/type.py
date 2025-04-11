from flambda_app.vos.base import Base
from datetime import datetime
from typing import Any, Dict, Optional


class Type(Base):
    """
    Object for Type
    """

    id: Optional[int]
    name: str
    status: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
    deleted_at: Optional[str]

    def __init__(self,
                 type_id: Optional[int] = None,
                 name: str = None,
                 status: Optional[str] = None,
                 created_at: Optional[str] = None,
                 updated_at: Optional[str] = None,
                 deleted_at: Optional[str] = None,
                 **kwargs: Any
                 ):

        self.id = type_id
        self.name = name
        self.status = status
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at
        self.deleted_at = deleted_at

        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __str__(self):
        """
        String representation of the Type instance.
        """
        return f"Type(id={self.id}, name={self.name}, status={self.status})"

    def to_dict(self) -> Dict[str, Optional[str]]:
        """
        Converts the Type to a dictionary.
        """
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'deleted_at': self.deleted_at
        }

    def to_api_response(self) -> Dict[str, str]:
        """
        Converts the Type to a dictionary for API responses.
        """
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status
        }
