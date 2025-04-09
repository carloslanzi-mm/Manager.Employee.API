from datetime import datetime
from typing import Dict, Optional, Any
from .base import Base

from flambda_app.repositories.v1.mysql.report_repository import ReportRepository


class Report(Base):
    """
    Object for Report
    """

    id: Optional[int]
    report_type_id: int
    url: str
    status: str
    created_at: Optional[str]
    updated_at: Optional[str]
    deleted_at: Optional[str]

    def __init__(self,
                 report_id: Optional[int] = None,
                 report_type_id: int = None,
                 url: str = None,
                 status: str = None,
                 created_at: Optional[str] = None,
                 updated_at: Optional[str] = None,
                 deleted_at: Optional[str] = None,
                 **kwargs: Any
                 ):

        self.id = report_id
        self.report_type_id = report_type_id
        self.url = url
        self.status = status
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at
        self.deleted_at = deleted_at

        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __str__(self):
        """
        String representation of the Report instance.
        """
        return f"Report(id={self.id}, status={self.status}"

    def get_report_type_name(self) -> Optional[str]:
        """Busca o nome da empresa usando CompanyService se não estiver no dicionário."""
        if not self.report_type_id:
            return None

        report_repository = ReportRepository()
        data = report_repository.get_entity('report_type',
                                            vo_class=ReportType,
                                            value=self.report_type_id,
                                            key='id',
                                            fields=['name'])

        return data.name if data else None

    def to_dict(self) -> Dict[str, Optional[str]]:
        """
        Converts the Report to a dictionary.
        """
        return {
            'id': self.id,
            'report_type_id': self.report_type_id,
            'url': self.url,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'deleted_at': self.deleted_at
        }

    def to_api_response(self) -> Dict[str, str]:
        return {
            'id': self.id,
            'url': self.url,
            'status': self.status,
            'created_at': self.created_at,
            'report_type': {
                'id': self.report_type_id,
                'name': self.get_report_type_name()},
        }


class ReportType(Base):
    """
    Object for ReportType
    """

    id: Optional[int]
    name: str
    created_at: Optional[str]
    updated_at: Optional[str]
    deleted_at: Optional[str]

    def __init__(self,
                 report_type_id: Optional[int] = None,
                 name: str = None,
                 created_at: Optional[str] = None,
                 updated_at: Optional[str] = None,
                 deleted_at: Optional[str] = None,
                 **kwargs: Any
                 ):

        self.id = report_type_id
        self.name = name
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at
        self.deleted_at = deleted_at

        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __str__(self):
        """
        String representation of the ReportType instance.
        """
        return f"ReportType(id={self.id}, name={self.name})"

    def to_dict(self) -> Dict[str, Optional[str]]:
        """
        Converts the ReportType to a dictionary.
        """
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'deleted_at': self.deleted_at
        }

    def to_api_response(self) -> Dict[str, str]:
        """
        Converts the ReportType to a dictionary for API responses.
        """
        return {
            'id': self.id,
            'name': self.name
        }
