"""
Módulo contendo o objeto Document, estendido de BaseDocumentFile, com campos de datas adicionais.
"""

from typing import Optional, Dict, Any
from flambda_app.vos.base import BaseDocumentFile


class Document(BaseDocumentFile):
    """
    Representa um documento com campos de data de início e fim adicionais.
    """
    update_allowed_fields = BaseDocumentFile.update_allowed_fields + ["started_at", "ended_at"]

    started_at: Optional[str]
    ended_at: Optional[str]

    def __init__(self,
                 started_at: Optional[str] = None,
                 ended_at: Optional[str] = None,
                 **kwargs: Any
                 ):
        """
        Inicializa um novo documento com datas opcionais de início e fim.
        """
        super().__init__(**kwargs)
        self.started_at = started_at
        self.ended_at = ended_at

    def to_dict(self) -> Dict[str, Optional[str]]:
        """
        Converte o documento para um dicionário.
        """
        base = super().to_dict()
        base.update({
            "started_at": self.started_at,
            "ended_at": self.ended_at
        })
        return base

    def to_api_response(self) -> Dict[str, Optional[str]]:
        """
        Converte o documento para um dicionário no formato de resposta da API.
        """
        base = super().to_api_response()
        base.update({
            "started_at": self.started_at,
            "ended_at": self.ended_at
        })
        return base
