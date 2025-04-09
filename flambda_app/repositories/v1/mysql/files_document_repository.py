"""
Módulo responsável por gerenciar operações relacionadas ao Files e Document.
"""

from flambda_app.repositories.v1.mysql import AbstractRepository


class FilesDocumentRepository(AbstractRepository):

    def __init__(self, logger=None, mysql_connection=None):
        """
        Inicializa o repositório da empresa, configurando o logger e a conexão com o banco de dados.

        Args:
            logger (Optional[Logger]): Instância do logger para registro de logs.
            mysql_connection (Optional[MySQLConnector]): Instância da conexão com MySQL.
        """
        super().__init__(logger, mysql_connection)
