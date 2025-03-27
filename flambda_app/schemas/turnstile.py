import uuid


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
