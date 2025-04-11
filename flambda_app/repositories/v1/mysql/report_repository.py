"""
Módulo responsável por gerenciar operações relacionadas ao relatório.
"""

from typing import List, Dict, Any, Optional
from flambda_app.request_control import Order, Pagination, PaginationType
from flambda_app.repositories.v1.mysql import AbstractRepository


class ReportRepository(AbstractRepository):

    def __init__(self, logger=None, mysql_connection=None):
        """
        Inicializa o repositório da empresa, configurando o logger e a conexão com o banco de dados.

        Args:
            logger (Optional[Logger]): Instância do logger para registro de logs.
            mysql_connection (Optional[MySQLConnector]): Instância da conexão com MySQL.
        """
        super().__init__(logger, mysql_connection)

    def list(self,
             where: dict,
             offset=None,
             limit=None,
             fields: list = None,
             sort_by=None,
             order_by=None,
             base_table: str = None,
             base_table_alias: str = None):
        """
        Retorna registros do banco com suporte a filtros, ordenação e paginação.

        Args:
            where (dict): Condições para o filtro.
            offset (int): Quantidade de registros a ignorar (paginação).
            limit (int): Máximo de registros a retornar.
            fields (list): Campos específicos a retornar.
            sort_by (str | list): Campo(s) para ordenação. Padrão: 'id'.
            order_by (str): Direção da ordenação ("ASC" ou "DESC"). Padrão: "ASC".
            base_table (str): Nome da tabela base. Padrão: `self.BASE_TABLE`.
            base_table_alias (str): Alias da tabela base. Padrão: `self.BASE_TABLE_ALIAS`.

        Returns:
            list | None: Lista de registros ou `None` em caso de erro.
        """
        table = base_table or self.BASE_TABLE
        alias = base_table_alias or self.BASE_TABLE_ALIAS

        if not fields:
            fields = '*'
        else:
            fields = [f"{alias}.{val}" for val in fields]
            fields = ",".join(fields)

        if order_by is None:
            order_by = Order.ASC

        if sort_by is None:
            sort_by = 'id'
        elif isinstance(sort_by, list):
            sort_by_arr = [f"{alias}.{val}" for val in sort_by]
            sort_by = ",".join(sort_by_arr)
        else:
            sort_by = f"{alias}.{sort_by}"

        sql = f"SELECT {fields} FROM {table} AS {alias}"

        values = []
        if where:
            where_str, values = self.build_where(where)
            sql += f" WHERE {where_str}"

        sql += f" ORDER BY {sort_by} {order_by}"

        if not offset:
            offset = Pagination.validate(PaginationType.OFFSET, offset)

        if not limit:
            limit = Pagination.validate(PaginationType.LIMIT, limit)

        sql += f" LIMIT {offset},{limit}"

        try:
            self.logger.info(f"SQL: {sql}")
            self.logger.info(f"SQL Values: {values}")
            result = self._execute(sql, values)
            result = result.fetchall()
        except Exception as err:
            self.logger.error(err)
            self._exception = err
            result = None
        finally:
            self._close()

        return result

    def count(self,
              where: dict,
              sort_by=None,
              order_by=None,
              base_table: str = None,
              base_table_alias: str = None):
        """
        Conta registros na tabela com base nos filtros.

        Args:
            where (dict): Filtros para a cláusula WHERE.
            sort_by (str | list): Campo(s) para ordenação.
            order_by (str): Direção da ordenação ('ASC' ou 'DESC').
            base_table (str): Nome da tabela base. Padrão: `self.BASE_TABLE`.
            base_table_alias (str): Alias da tabela. Padrão: `self.BASE_TABLE_ALIAS`.

        Returns:
            int: Total de registros encontrados.
        """

        table = base_table or self.BASE_TABLE
        alias = base_table_alias or self.BASE_TABLE_ALIAS

        if order_by is None:
            order_by = Order.ASC

        if sort_by is None:
            sort_by = 'id'
        elif isinstance(sort_by, list):
            sort_by_arr = [f"{alias}.{val}" for val in sort_by]
            sort_by = ",".join(sort_by_arr)
        else:
            sort_by = f"{alias}.{sort_by}"

        sql = f"SELECT COUNT(1) AS total FROM {table} AS {alias}"

        values = []
        if where:
            where_str, values = self.build_where(where)
            sql += f" WHERE {where_str}"

        sql += f" ORDER BY {sort_by} {order_by}"

        try:
            self.logger.info(f"SQL: {sql}")
            self.logger.info(f"SQL Values: {values}")
            result = self._execute(sql, values)
            result = result.fetchone()
            result = result['total']
        except Exception as err:
            self.logger.error(err)
            self._exception = err
            result = 0
        finally:
            self._close()

        return result

    def list_entity_report(self, company_ids: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        """
        Gera um relatório com dados da empresa, endereço, documentos e arquivos.

        Args:
            company_ids (List[int], opcional): Lista de IDs das empresas a serem filtradas.

        Returns:
            List[Dict[str, Any]]: Lista de registros formatados para o relatório.
        """

        sql = """
            SELECT
                c.name AS nome_empresa,
                DATE_FORMAT(c.created_at, '%Y-%m-%d') AS data_criacao_empresa,
                DATE_FORMAT(c.updated_at, '%Y-%m-%d') AS ultima_atualizacao_empresa,

                a.street AS rua,
                a.number AS numero,
                a.neighbor AS bairro,
                a.zip_code AS cep,
                DATE_FORMAT(a.updated_at, '%Y-%m-%d') AS ultima_atualizacao_endereco,

                d.name AS nome_documento,
                d.url AS link_documento,
                DATE_FORMAT(d.started_at, '%Y-%m-%d') AS inicio_documento,
                DATE_FORMAT(d.ended_at, '%Y-%m-%d') AS fim_documento,
                DATE_FORMAT(d.updated_at, '%Y-%m-%d') AS ultima_atualizacao_documento,
                td.name AS tipo_documento,
                td.status AS status_tipo_documento,
                DATE_FORMAT(td.updated_at, '%Y-%m-%d') AS ultima_atualizacao_tipo_documento,

                f.name AS nome_arquivo,
                f.url AS link_arquivo,
                DATE_FORMAT(f.updated_at, '%Y-%m-%d') AS ultima_atualizacao_arquivo,
                tf.name AS tipo_arquivo,
                tf.status AS status_tipo_arquivo,
                DATE_FORMAT(tf.updated_at, '%Y-%m-%d') AS ultima_atualizacao_tipo_arquivo

            FROM company c
            LEFT JOIN address a ON a.company_id = c.id
            LEFT JOIN documents d ON d.company_id = c.id
            LEFT JOIN type td ON td.id = d.type_id
            LEFT JOIN files f ON f.company_id = c.id
            LEFT JOIN type tf ON tf.id = f.type_id
        """

        # Adiciona cláusula WHERE apenas se company_ids for fornecido
        if company_ids:
            placeholders = ', '.join(str(int(company_id)) for company_id in company_ids)
            sql += f"\nWHERE c.id IN ({placeholders})"

        try:
            result = self._execute(sql)
            rows = result.fetchall()
            return rows or []

        except Exception as err:
            self.logger.error(f"[list_entity_report] Erro ao buscar relatório: {err}")
            self._exception = err
            return []

        finally:
            self._close()
