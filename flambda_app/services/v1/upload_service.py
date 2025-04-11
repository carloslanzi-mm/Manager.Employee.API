"""
Módulo responsável por gerenciar operações relacionadas a empresas.
"""
import os
from typing import Optional, Tuple, List
from uuid import uuid4

from flambda_app.database.mysql import MySQLConnector
from flambda_app.database.redis import RedisConnector
from flambda_app.logging import get_logger
from flambda_app.vos.document import Document
from flambda_app.vos.file import File

from flambda_app.repositories.v1.mysql.company_repository import CompanyRepository


class UploadService:
    """
    Camada de serviço para gerenciamento de operações da Empresa.
    """

    debug_mode = False
    REDIS_ENABLED = False

    def __init__(self, logger=None, mysql_connector=None, redis_connector=None,
                 company_repository=None):
        """
        Serviço para gerenciar operações relacionadas à empresa.

       Args:
           logger (Optional[Logger]): Instância do logger.
           mysql_connector (Optional[MySQLConnector]): Conector do MySQL.
           redis_connector (Optional[RedisConnector]): Conector do Redis.
           company_repository (Optional[CompanyRepository]): Repositório de empresas no MySQL.
       """
        # logger
        self.logger = logger if logger is None else get_logger()
        # database connection
        self.mysql_connector = mysql_connector if mysql_connector is not None else MySQLConnector()
        # mysql repository
        self.company_repository = company_repository if company_repository is not None \
            else CompanyRepository(mysql_connection=self.mysql_connector.get_connection())

        # exception
        self.exception = None

        if self.REDIS_ENABLED:
            # redis connection
            self.redis_connector = redis_connector if redis_connector is not None \
                else RedisConnector()
            # redis repository
            self.redis_upload_repository = None

        self.debug(self.debug_mode)

    def debug(self, flag: bool = False):
        """
        Ativa ou desativa o modo de depuração.

        Args:
            flag (bool): Define se o modo de depuração será ativado ou desativado.
        """
        self.debug_mode = flag
        self.company_repository.debug = self.debug_mode
        if self.REDIS_ENABLED:
            self.redis_upload_repository.debug = self.debug_mode

    @staticmethod
    def _upload_single_file(file, bucket_name: str, s3_aws) -> Optional[Tuple[str, str]]:
        """
        Faz upload de um único arquivo para o S3 e retorna nome e URL pública.

        Returns:
            Tuple (nome do arquivo, URL pública) ou None em caso de falha.
        """
        original_name, extension = os.path.splitext(file.filename)
        object_name = f"{original_name}_{str(uuid4())}{extension}"
        response = s3_aws.upload_filedata(bucket_name, file, object_name)

        if response is None:
            return None

        file_url = s3_aws.get_public_url(bucket_name, object_name)
        return object_name, file_url

    def _rollback_uploaded_files(self, object_names: List[str], bucket_name: str, s3_aws) -> None:
        """
        Remove arquivos do S3 em caso de erro no processo de upload.
        """
        for obj in object_names:
            try:
                s3_aws.delete_object(bucket_name, obj)
            except (OSError, RuntimeError) as err:
                self.logger.error(f"Erro ao remover {obj} no rollback: {err}")

    def upload_and_save_files(self, files, company_id: int, storage_type: str,
                              required_fields: dict, s3_aws) -> Tuple[dict, int]:
        """
        Faz o upload de arquivos para o S3 e salva os metadados no banco de dados.

        Args:
            files: Lista de arquivos enviados via formulário.
            company_id (int): ID da empresa relacionada aos arquivos.
            storage_type (str): Tipo de armazenamento ('files' ou 'documents').
            required_fields (dict): Campos obrigatórios.
            s3_aws: Cliente S3 com métodos de upload, deleção e geração de URL pública.
        """
        entity_class = File if storage_type == 'files' else Document
        table = 'files' if storage_type == 'files' else 'documents'
        bucket_name = os.getenv("APP_BUCKET")

        uploaded = []
        database_entries = []

        for idx, file in enumerate(files):
            upload_result = self._upload_single_file(file, bucket_name, s3_aws)
            if upload_result is None:
                self._rollback_uploaded_files(uploaded, bucket_name, s3_aws)
                return {'error': 'Erro ao enviar os arquivos. Nenhum foi salvo.'}, 500

            object_name, file_url = upload_result
            uploaded.append(object_name)

            entity_kwargs = {
                'company_id': company_id,
                'name': object_name,
                'type_id': int(required_fields['type_ids'][idx]),
                'url': file_url
            }

            if storage_type == 'documents':
                entity_kwargs.update({
                    'started_at': required_fields['started_at'][idx],
                    'ended_at': required_fields['ended_at'][idx],
                })

            entity = entity_class(**entity_kwargs)
            success, file_id = self.company_repository.create_entity(entity, table, 'id')

            if success:
                database_entries.append({"id": file_id, "name": object_name, "url": file_url})
            else:
                return {'error': f'Erro ao salvar {object_name} no banco de dados.'}, 500

        return {
            'mensagem': f'{len(database_entries)} arquivo(s) enviados e salvos com sucesso!',
            'arquivos': database_entries
        }, 200

    def delete_uploaded_files(self, ids: list, company_id: int, storage_type: str):
        """
        Deleta arquivos associados a uma empresa com base no tipo de armazenamento e IDs fornecidos.

        Args:
            ids (list): Lista de IDs dos arquivos a serem deletados.
            company_id (int): ID da empresa dona dos arquivos.
            storage_type (str): Tipo de armazenamento ('files' ou 'documents').
        """
        entity_class = File if storage_type == 'files' else Document
        table = 'files' if storage_type == 'files' else 'documents'

        company_repo = CompanyRepository()
        deleted_files = []

        for file_id in ids:
            entity = company_repo.get_entity(
                table_name=table,
                vo_class=entity_class,
                value=file_id,
                where={"deleted_at": None}
            )

            if not entity or entity.company_id != company_id:
                continue

            success = company_repo.delete_entity(table, "id", file_id)
            if success:
                deleted_files.append({"id": file_id, "name": entity.name})
            else:
                self.logger.error(f"Erro ao deletar arquivo id={file_id} nome={entity.name}")

        if not deleted_files:
            return {'error': 'Nenhum arquivo foi deletado.'}, 404

        return {
            'mensagem': f'{len(deleted_files)} arquivo(s) deletado(s) com sucesso!',
            'arquivos': deleted_files
        }, 200
