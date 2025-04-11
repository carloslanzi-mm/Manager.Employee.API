"""
Módulo responsável por gerenciar operações relacionadas ao upload.
"""

from datetime import datetime
from flambda_app.config import get_config
from flambda_app.logging import get_logger
from flambda_app.services.v1.upload_service import UploadService
from flambda_app.http_resources.request import ApiRequest


class UploadManager:
    """
    Classe responsável por gerenciar operações relacionadas ao upload.
    """

    def __init__(self, logger=None, config=None, upload_service=None):
        """
        Inicializa a instância do UploadManager.

        :param logger: Logger opcional, usa get_logger() por padrão.
        :param config: Configuração opcional, usa get_config() por padrão.
        :param upload_service: Serviço de upload opcional, usa CompanyService() por padrão.
        """
        self.logger = logger if logger is not None else get_logger()
        # configurations
        self.config = config if config is not None else get_config()
        # service
        self.upload_service = upload_service if upload_service is not None else UploadService(
            self.logger)

        # exception
        self.exception = None

        # debug
        self.debug_mode = None

    def debug(self, flag: bool = False):
        """
       Define o modo de depuração.

       :param flag: Se True, ativa o modo de depuração.
       """
        self.debug_mode = flag
        self.upload_service.debug(self.debug_mode)

    def count(self, request: ApiRequest) -> int:
        """
        Obtém o total de upload com base na requisição.

        :param request: Objeto de requisição.
        :return: Número total de empresas.
        """
        total = self.upload_service.count(request.to_dict())
        if self.upload_service.exception:
            self.exception = self.upload_service.exception
            raise self.exception
        return total

    def process_file_upload(self, flask_request, company_id: int, storage_type: str, s3_aws):
        """
        Processa o upload de arquivos para uma empresa, validando os campos obrigatórios
        e encaminhando para o serviço de upload.

        Args:
            flask_request: Requisição Flask com os arquivos e dados do formulário.
            company_id: ID da empresa.
            storage_type: Tipo de armazenamento ('files' ou 'documents').
            s3_aws: Cliente ou config do AWS S3.

        Returns:
            Tuple com dicionário de resposta e código HTTP.
        """
        self.logger.info(f"{flask_request.remote_addr} - "
                         f"[{datetime.now().strftime('%d/%b/%Y %H:%M:%S')}]"
                         f" \"{flask_request.method} {flask_request.full_path}\"")

        if 'files' not in flask_request.files:
            return {'error': 'Nenhum arquivo foi enviado'}, 400

        if storage_type not in ["files", "documents"]:
            return {'error': "O storage_type deve ser 'files' ou 'documents'"}, 400

        files = flask_request.files.getlist('files')

        required_fields = {
            'type_ids': flask_request.form.getlist('type_ids'),
        }

        if storage_type == 'documents':
            required_fields['started_at'] = flask_request.form.getlist('started_at')
            required_fields['ended_at'] = flask_request.form.getlist('ended_at')

        for field_name, field_values in required_fields.items():
            if not field_values:
                return {'error': f'O campo {field_name} é obrigatório'}, 400
            if len(field_values) != len(files):
                return {
                    'error': f'Campo {field_name} deve ter o mesmo número de itens que os arquivos'
                }, 400

        return self.upload_service.upload_and_save_files(
            files, company_id, storage_type, required_fields, s3_aws
        )

    def process_file_deletion(self, data: dict, company_id: int, storage_type: str):
        """
        Processa a deleção de arquivos enviados.
        """
        if not data or 'ids' not in data:
            return {'error': 'A lista de IDs deve ser fornecida no corpo da requisição'}, 400

        ids = data['ids']
        if not isinstance(ids, list) or not ids:
            return {'error': 'O campo ids não pode ser uma lista vazia'}, 400

        if storage_type not in ["files", "documents"]:
            return {'error': "O storage_type deve ser 'files' ou 'documents'"}, 400

        return self.upload_service.delete_uploaded_files(ids, company_id, storage_type)
