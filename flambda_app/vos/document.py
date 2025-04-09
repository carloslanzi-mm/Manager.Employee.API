from typing import Optional, Dict, Any
from .base import BaseDocumentFile


class Document(BaseDocumentFile):
    update_allowed_fields = BaseDocumentFile.update_allowed_fields + ["started_at", "ended_at"]

    started_at: Optional[str]
    ended_at: Optional[str]

    def __init__(self,
                 started_at: Optional[str] = None,
                 ended_at: Optional[str] = None,
                 **kwargs: Any
                 ):
        super().__init__(**kwargs)
        self.started_at = started_at
        self.ended_at = ended_at

    def to_dict(self) -> Dict[str, Optional[str]]:
        base = super().to_dict()
        base.update({
            "started_at": self.started_at,
            "ended_at": self.ended_at
        })
        return base

    def to_api_response(self) -> Dict[str, Optional[str]]:
        base = super().to_api_response()
        base.update({
            "started_at": self.started_at,
            "ended_at": self.ended_at
        })
        return base
