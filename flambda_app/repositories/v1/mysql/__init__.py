"""
Mysql Repositories Module for Flambda APP
Version: 1.0.0
"""
from flambda_app.database.mysql import MySQLConnector
from flambda_app.logging import get_logger
from flambda_app.request_control import Pagination, PaginationType
import pymysql


class AbstractRepository:
    def __init__(self, logger, mysql_connection):
        self.logger = logger if logger is not None else get_logger()
        # todo utilizar connector
        self.connection = mysql_connection if mysql_connection is not None else MySQLConnector().get_connection()
        self._exception = None
        self.debug = False

    def get_connection(self):
        return self.connection

    def get_exception(self):
        return self._exception

    def _execute(self, sql, params=None):
        if self.debug:
            self.logger.info("SQL: {}".format(sql))
            self.logger.info("SQL Values: {}".format(params))

        # issubclass(connection_mock.__class__, pymysql.connections.Connection)
        if isinstance(self.connection, pymysql.connections.Connection) \
            or issubclass(self.connection.__class__, pymysql.connections.Connection):
            # always connect because is treadsafe
            self.connection.connect()
            # with self.connection.cursor() as cursor:
            cursor = self.connection.cursor()
            cursor.execute(sql, params)
            result = cursor
            # close connection only in read
            # self.connection.close()
        else:
            result = self.connection.execute(sql, params)
        return result

    def _close(self):
        self.connection.close()

    def build_where(self, where: dict, alias: str = None):
        conditions = []
        values = []

        for key, value in where.items():
            column = f"{alias}.{key}" if alias else key
            if value is None:
                conditions.append(f"{column} IS NULL")
            else:
                conditions.append(f"{column} = %s")
                values.append(value)

        where_clause = " AND ".join(conditions)
        return where_clause, values

    def create_entity(self, entity, table_name, primary_key="id"):
        """
        Insere um novo registro no banco de dados.

        Args:
            entity: Objeto representando a entidade a ser inserida.
            table_name (str): Nome da tabela onde o dado será inserido.
            primary_key (str, optional): Nome da chave primária a ser ignorada na inserção.

        Returns:
            Tuple[bool, Optional[int]]: Retorna um tuple com:
                - `True` se a inserção for bem-sucedida, `False` caso contrário.
                - O ID do registro inserido ou `None` em caso de erro.
        """
        entity_dict = entity.to_dict()

        if primary_key in entity_dict:
            del entity_dict[primary_key]  # Remover a chave primária para não inserir

        keys = list(entity_dict.keys())
        keys_str = ",".join(keys)
        values_str = ",".join(['%s' for _ in range(len(keys))])
        values = tuple(entity_dict.values())

        sql = f"INSERT INTO {table_name} ({keys_str}) VALUES ({values_str})"

        try:
            self._execute(sql, values)
            entity.id = self.connection.insert_id()  # Captura o último ID inserido
            self.connection.commit()
            return True, entity.id

        except Exception as err:
            self.logger.error(err)
            self.connection.rollback()
            self._exception = err
            return False, None

        finally:
            self._close()

    def update_entity(self, entity, table_name, key_column, key_value, ignore_keys=None):
        """
        Atualiza um registro no banco de dados.

        Args:
            entity: Objeto contendo os dados a serem atualizados.
            table_name (str): Nome da tabela onde o dado será atualizado.
            key_column (str): Nome da coluna usada como chave (ex: "id" ou "uuid").
            key_value (Any): Valor correspondente ao campo chave.
            ignore_keys (list, optional): Lista de colunas a serem ignoradas na atualização.

        Returns:
            bool: `True` se a atualização for bem-sucedida, `False` caso contrário.
        """
        entity_dict = entity.to_dict()

        if ignore_keys is None:
            ignore_keys = ["id", "uuid", "created_at"]

        # Remover colunas que não devem ser atualizadas
        for key in ignore_keys:
            entity_dict.pop(key, None)

        # Preparando os dados para a query
        set_statements = ", ".join([f"{key} = %s" for key in entity_dict.keys()])
        values = list(entity_dict.values()) + [key_value]

        sql = f"UPDATE {table_name} SET {set_statements} WHERE {key_column} = %s"

        try:
            updated = self._execute(sql, values)
            if updated:
                self.connection.commit()
                return True
        except Exception as err:
            self.logger.error(err)
            self.connection.rollback()
            self._exception = err
            return False
        finally:
            self._close()

    def delete_entity(self, table_name, key, value, soft_delete=True,
                      deleted_at_column="deleted_at"):
        """
        Deleta logicamente ou fisicamente um registro de uma tabela.

        Args:
            table_name (str): Nome da tabela.
            key (str): Nome do campo usado na cláusula WHERE.
            value (Any): Valor da chave para encontrar o registro.
            soft_delete (bool): Se True, faz uma exclusão lógica (marca como deletado).
            deleted_at_column (str): Nome da coluna usada para a exclusão lógica.

        Returns:
            bool: True se a exclusão for bem-sucedida, False caso contrário.
        """
        try:
            if soft_delete:
                sql = f"UPDATE {table_name} SET {deleted_at_column} = NOW() WHERE {key} = %s"
                self._execute(sql, (value,))
            else:
                sql = f"DELETE FROM {table_name} WHERE {key} = %s"
                self._execute(sql, (value,))

            self.connection.commit()
            return True

        except Exception as err:
            self.logger.error(f"Erro ao deletar entidade: {err}")
            self.connection.rollback()
            self._exception = err
            return False

        finally:
            self._close()

    def get_entity(self, table_name, vo_class, value, key="id", where: dict = None,
                   fields: list = None):
        """
        Obtém um registro de uma tabela genérica no banco de dados.

        Args:
            table_name (str): Nome da tabela.
            vo_class (Type): Classe VO (Value Object) para instanciar com os resultados.
            value (Any): Valor do campo de busca (por exemplo, ID).
            key (str, optional): Nome da coluna utilizada como chave para a busca. Padrão é 'id'.
            where (dict, optional): Condições adicionais em formato de dicionário.
            fields (list, optional): Lista de campos específicos a serem retornados.

        Returns:
            vo_class | None: Instância da VO preenchida com os dados ou None se não encontrado.
        """
        try:
            if where is None:
                where = {}

            if fields is None or len(fields) == 0:
                fields_str = '*'
            else:
                fields_str = ",".join(fields)

            sql = f"SELECT {fields_str} FROM {table_name} WHERE {key} = %s"
            values = [value]

            for k, v in where.items():
                if v is None:
                    sql += f" AND {k} IS NULL"
                else:
                    sql += f" AND {k} = %s"
                    values.append(v)

            result = self._execute(sql, values)
            item = result.fetchone()

            if item:
                return vo_class(**item)

        except Exception as err:
            self.logger.error(f"Erro ao buscar entidade: {err}")

        finally:
            self._close()

        return None

    def list_entities(
        self,
        table_name,
        vo_class=None,
        where: dict = None,
        offset=None,
        limit=None,
        fields: list = None,
        sort_by=None,
        order_by="ASC"
    ):
        """
        Lista registros de uma tabela genérica no banco de dados com filtros, ordenação e paginação.

        Args:
            table_name (str): Nome da tabela.
            vo_class (Type, optional): Classe VO (Value Object) para mapear os resultados. Se None, retorna dicts.
            where (dict, optional): Condições para a cláusula WHERE.
            offset (int, optional): Offset para paginação.
            limit (int, optional): Limite de registros retornados.
            fields (list, optional): Lista de campos a retornar. Se None, retorna todos.
            sort_by (str | list, optional): Campo(s) para ordenação. Se None, ordena por 'id'.
            order_by (str, optional): Direção da ordenação. Padrão é 'ASC'.

        Returns:
            list: Lista de registros (VO ou dict), ou [] se nenhum encontrado.
        """
        alias = "t"  # Alias padrão
        self.BASE_TABLE_ALIAS = alias  # Para reaproveitar build_where
        self.BASE_TABLE = table_name  # Para reaproveitar build_where

        if fields is None or len(fields) == 0:
            fields_str = "*"
        else:
            fields_str = ", ".join(f"{alias}.{field}" for field in fields)

        if not sort_by:
            sort_by_str = f"{alias}.id"
        elif isinstance(sort_by, list):
            sort_by_str = ", ".join(f"{alias}.{field}" for field in sort_by)
        else:
            sort_by_str = f"{alias}.{sort_by}"

        if not offset:
            offset = Pagination.validate(PaginationType.OFFSET, offset)

        if not limit:
            limit = Pagination.validate(PaginationType.LIMIT, limit)

        sql = f"SELECT {fields_str} FROM {table_name} AS {alias}"

        if where:
            where_str = self.build_where(where)
            sql += f" WHERE {where_str}"

        sql += f" ORDER BY {sort_by_str} {order_by}"
        sql += f" LIMIT {offset}, {limit}"

        try:
            result = self._execute(sql)
            rows = result.fetchall()

            if not rows:
                return []

            if vo_class:
                return [vo_class(**row) for row in rows]

            return rows

        except Exception as err:
            self.logger.error(f"[list_entities] Erro ao listar registros de {table_name}: {err}")
            self._exception = err
            return []

        finally:
            self._close()
