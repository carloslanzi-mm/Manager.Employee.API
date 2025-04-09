from datetime import datetime
from typing import Optional, Dict, Any
from .base import Base


class Address(Base):
    """
    Value Object para representar um endereço.
    """
    update_allowed_fields = ["street", "number", "neighbor", "zip_code", "updated_at",
                             "deleted_at"]

    id: Optional[int]
    street: Optional[str]
    number: Optional[str]
    neighbor: Optional[str]
    zip_code: Optional[str]
    created_at: str
    updated_at: Optional[str]
    deleted_at: Optional[str]
    company_id: Optional[int]

    def __init__(self,
                 address_id: Optional[int] = None,
                 street: Optional[str] = None,
                 number: Optional[str] = None,
                 neighbor: Optional[str] = None,
                 zip_code: Optional[str] = None,
                 created_at: Optional[str] = None,
                 updated_at: Optional[str] = None,
                 deleted_at: Optional[str] = None,
                 company_id: Optional[int] = None,
                 **kwargs: Any
                 ):
        self.id = address_id
        self.street = street
        self.number = number
        self.neighbor = neighbor
        self.zip_code = zip_code
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at
        self.deleted_at = deleted_at
        self.company_id = company_id

        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __str__(self):
        return f"AddressVO(id={self.id}, street={self.street}, number={self.number}, " \
               f"neighbor={self.neighbor}, zip_code={self.zip_code}, " \
               f"company_id={self.company_id}, created_at={self.created_at}, " \
               f"updated_at={self.updated_at}, deleted_at={self.deleted_at})"

    def to_dict(self) -> Dict[str, Optional[str]]:
        return {
            'id': self.id,
            'street': self.street,
            'number': self.number,
            'neighbor': self.neighbor,
            'zip_code': self.zip_code,
            'company_id': self.company_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'deleted_at': self.deleted_at
        }

    def to_api_response(self) -> Dict[str, Optional[str]]:
        return {
            "id": self.id,
            "street": self.street,
            "number": self.number,
            "neighbor": self.neighbor,
            "zip_code": self.zip_code
        }
