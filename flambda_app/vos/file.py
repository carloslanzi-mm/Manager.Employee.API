"""
Módulo que define o Value Object (VO) File, representando um arquivo associado a uma empresa.
"""

from flambda_app.vos.base import BaseDocumentFile


class File(BaseDocumentFile):
    """
    Object que representa um arquivo genérico vinculado à empresa,
    herdando os atributos e métodos de BaseDocumentFile.
    """
