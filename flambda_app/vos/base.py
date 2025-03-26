class Base:
    update_allowed_fields = []

    def update(self, data: dict):
        """
        Atualiza a instância com os dados fornecidos.

        Args:
            data (dict): Dados para atualização.
        """
        for field in self.update_allowed_fields:
            if field in data:
                setattr(self, field, data[field])
