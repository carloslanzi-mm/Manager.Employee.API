"""
Product Value Object Module for Flambda APP
Version: 1.0.0
"""
import uuid

from flambda_app.helper import datetime_now_with_timezone
from flambda_app.vos import AbstractVO


class CompanyVO(AbstractVO):
    """

    """

    def __init__(self, data: dict = None, default_values=True):
        """
        Always the dateobjects must be datetime instances
        """
        self.id = data.get('id') if data and "id" in data else None
        self.uuid = data.get('uuid') if data and "uuid" in data else \
            str(uuid.uuid4()) if default_values is True else None
        self.name = data.get('name') if data and "name" in data else None
        self.created_at = data.get('created_at') if data and 'created_at' in data \
            else datetime_now_with_timezone() if default_values is True else None
        self.updated_at = data.get('updated_at') if data and 'updated_at' in data else None
        self.deleted_at = data.get('deleted_at') if data and 'deleted_at' in data else None
