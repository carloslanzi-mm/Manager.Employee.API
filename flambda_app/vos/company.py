import uuid as python_uuid
from datetime import datetime
from typing import Dict, Optional, Any
from .base import Base
from flambda_app.helper import validate_cnpj


class CompanyVO(Base):
    """
    Object for Company
    """
    update_allowed_fields = [
        "name", "created_at", "updated_at", "deleted_at", "contact_phone", "contact_email",
        "contact_person", "service_type", "partnership_started_at", "bank_name",
        "agency", "account_number", "account_type", "cnpj"
    ]

    required_fields = [
        "name", "contact_phone", "contact_email", "contact_person", "service_type",
        "partnership_started_at", "cnpj"
    ]

    filter_allowed_fields = [
        "name", "contact_phone", "contact_email", "contact_person", "service_type",
        "partnership_started_at", "cnpj", "created_at"
    ]

    custom_validators = {
        "cnpj": validate_cnpj
    }

    id: Optional[int]
    uuid: str
    name: Optional[str]
    contact_phone: Optional[str]
    contact_email: Optional[str]
    contact_person: Optional[str]
    service_type: Optional[str]
    partnership_started_at: Optional[str]
    bank_name: Optional[str]
    agency: Optional[str]
    account_number: Optional[str]
    account_type: Optional[str]
    cnpj: Optional[str]
    created_at: str
    updated_at: Optional[str]
    deleted_at: Optional[str]

    def __init__(self,
                 company_id: Optional[int] = None,
                 uuid: Optional[str] = None,
                 name: Optional[str] = None,
                 contact_phone: Optional[str] = None,
                 contact_email: Optional[str] = None,
                 contact_person: Optional[str] = None,
                 service_type: Optional[str] = None,
                 partnership_started_at: Optional[str] = None,
                 bank_name: Optional[str] = None,
                 agency: Optional[str] = None,
                 account_number: Optional[str] = None,
                 account_type: Optional[str] = None,
                 cnpj: Optional[str] = None,
                 created_at: Optional[str] = None,
                 updated_at: Optional[str] = None,
                 deleted_at: Optional[str] = None,
                 **kwargs: Any
                 ):

        self.id = company_id
        self.uuid = uuid or str(python_uuid.uuid4())
        self.name = name
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at
        self.deleted_at = deleted_at
        self.contact_phone = contact_phone
        self.contact_email = contact_email
        self.contact_person = contact_person
        self.service_type = service_type
        self.partnership_started_at = partnership_started_at
        self.bank_name = bank_name
        self.agency = agency
        self.account_number = account_number
        self.account_type = account_type
        self.cnpj = cnpj

        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __str__(self):
        """
        String representation of the CompanyVO instance.
        """
        return f"CompanyVO(id={self.id}, uuid={self.uuid}, name={self.name}, " \
               f"created_at={self.created_at}, updated_at={self.updated_at}, " \
               f"deleted_at={self.deleted_at}, contact_phone={self.contact_phone}, " \
               f"contact_email={self.contact_email}, contact_person={self.contact_person}, " \
               f"service_type={self.service_type}, partnership_started_at={self.partnership_started_at}, " \
               f"bank_name={self.bank_name}, agency={self.agency}, " \
               f"account_number={self.account_number}, account_type={self.account_type}, " \
               f"cnpj={self.cnpj})"

    def to_dict(self) -> Dict[str, Optional[str]]:
        """
        Converts the CompanyVO to a dictionary.
        """
        return {
            'id': self.id,
            'uuid': self.uuid,
            'name': self.name,
            'contact_phone': self.contact_phone,
            'contact_email': self.contact_email,
            'contact_person': self.contact_person,
            'service_type': self.service_type,
            'partnership_started_at': self.partnership_started_at,
            'bank_name': self.bank_name,
            'agency': self.agency,
            'account_number': self.account_number,
            'account_type': self.account_type,
            'cnpj': self.cnpj,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'deleted_at': self.deleted_at
        }

    def to_api_response(self) -> Dict[str, str]:
        return {
            "id": self.id,
            "uuid": self.uuid,
            'name': self.name,
            'contact_phone': self.contact_phone,
            'contact_email': self.contact_email,
            'contact_person': self.contact_person,
            'service_type': self.service_type,
            'partnership_started_at': self.partnership_started_at,
            'bank_name': self.bank_name,
            'agency': self.agency,
            'account_number': self.account_number,
            'account_type': self.account_type,
            'cnpj': self.cnpj,
        }
