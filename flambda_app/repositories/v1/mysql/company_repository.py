"""
Módulo responsável por gerenciar operações relacionadas a empresa.
"""

from datetime import datetime

from flambda_app.request_control import Order, Pagination, PaginationType
from flambda_app.repositories.v1.mysql import AbstractRepository
from flambda_app.vos.address import Address
from flambda_app.vos.company import CompanyVO


class CompanyRepository(AbstractRepository):
    """
    Repositório para operações no banco de dados relacionadas à entidade Empresa.

    A classe `CompanyRepository` fornece métodos para interagir com a tabela de empresas
    no banco de dados MySQL, utilizando a estrutura definida em `AbstractRepository`.

    Atributos:
        BASE_TABLE (str): Nome da tabela no banco de dados.
        BASE_SCHEMA (str): Nome do esquema do banco de dados.
        BASE_TABLE_ALIAS (str): Alias utilizado para a tabela em consultas SQL.
        PK (str): Nome da chave primária da tabela.
        UUID_KEY (str): Nome do campo UUID usado para identificação única.

    Args:
        logger (Optional[Logger]): Instância do logger para registrar eventos e erros.
        mysql_connection (Optional[MySQLConnector]): Conexão com o banco de dados MySQL.
    """
    BASE_TABLE = 'company'
    BASE_SCHEMA = 'store'
    BASE_TABLE_ALIAS = 'c'
    PK = 'id'
    UUID_KEY = 'uuid'

    def __init__(self, logger=None, mysql_connection=None):
        """
        Inicializa o repositório da empresa, configurando o logger e a conexão com o banco de dados.

        Args:
            logger (Optional[Logger]): Instância do logger para registro de logs.
            mysql_connection (Optional[MySQLConnector]): Instância da conexão com MySQL.
        """
        super().__init__(logger, mysql_connection)

    # Tavares
    def create_with_address(self, company: CompanyVO, address: Address):
        """
        Cria a empresa e, se bem-sucedido, insere o endereço associado.

        Args:
            company (CompanyVO): Objeto representando a empresa.
            address (Address): Objeto representando o endereço da empresa.

        Returns:
            Tuple[bool, Optional[int]]: Retorna um tuple com:
                - `True` se ambos os registros forem inseridos com sucesso.
                - O ID da empresa criada.
        """
        created, company_id = self.create(company)
        if not created:
            return False

        address.company_id = company_id

        created, address_id = self.create_entity(address, "address", "id")

        return created if created else False

    def create(self, company: CompanyVO):
        """
        Insere um novo registro de empresa no banco de dados.

        Este método recebe um objeto `CompanyVO`, extrai seus atributos (exceto a chave primária),
        e insere os valores correspondentes na tabela de empresas.

        Args:
            company (CompanyVO): Objeto contendo os dados da empresa a serem inseridos.

        Returns:
            bool: `True` se a inserção for bem-sucedida, `False` caso contrário.

        Raises:
            Exception: Captura e registra qualquer erro ocorrido durante a inserção.
        """
        keys = list(company.to_dict().keys())
        # Remover a PK
        keys.remove(self.PK)
        keys_str = ",".join(keys)
        values_count = len(company.to_dict().values()) - 1  # Excluindo a PK
        values_str = ",".join(['%s' for _ in range(values_count)])

        # Query
        sql = "INSERT INTO {} ({}) VALUES ({})".format(self.BASE_TABLE, keys_str, values_str)

        # Tratamentos finais
        company_dict = company.to_dict()
        del company_dict[self.PK]
        values = tuple(company_dict.values())

        # Tentando criar
        try:
            self._execute(sql, values)
            # Pegando o último id inserido
            company.id = self.connection.insert_id()
            # Commit
            self.connection.commit()

            # Em caso de sucesso, retorne True
            return True, company.id

        except Exception as err:
            self.logger.error(err)
            self.connection.rollback()
            self._exception = err
            return False, None

        finally:
            self._close()

    def update(self, company: CompanyVO, value, key=None):
        """
        Atualiza um registro de empresa no banco de dados.

        Este método recebe um objeto `CompanyVO` e atualiza os campos informados na tabela de
        empresas, utilizando um campo chave (`key`) para identificar o registro a ser alterado.

        Args:
            company (CompanyVO): Objeto contendo os dados atualizados da empresa.
            value (Any): Valor correspondente ao campo `key` utilizado na cláusula WHERE.
            key (str, optional): Nome do campo utilizado como chave para a atualização.
                                 Caso não seja informado, será utilizada a chave primária (`PK`).

        Returns:
            bool: `True` se a atualização for bem-sucedida, `False` caso contrário.

        Raises:
            Exception: Captura e registra qualquer erro ocorrido durante a atualização.
        """
        key_type = '%s'
        if key is None:
            key = self.PK

        keys = list(company.to_dict().keys())
        # Remover a PK
        keys.remove(self.PK)
        # Remover o UUID
        keys.remove(self.UUID_KEY)

        # Preparando os valores
        values = []
        update_data = []
        for k_key, val in company.to_dict().items():
            if k_key in keys:
                update_data.append('{}.{}=%s'.format(self.BASE_TABLE_ALIAS, k_key))
                values.append(val)

        update_str = ",".join(update_data)
        # Query
        sql = "UPDATE {} as {} SET {} WHERE {}.{} = {}".format(self.BASE_TABLE,
                                                               self.BASE_TABLE_ALIAS, update_str,
                                                               self.BASE_TABLE_ALIAS, key, key_type)

        # Tratamentos finais
        company_dict = company.to_dict()
        del company_dict[self.PK]
        del company_dict[self.UUID_KEY]
        values.append(value)

        try:
            updated = self._execute(sql, values)
            if updated:  # Se a execução foi bem-sucedida, retorne True
                self.connection.commit()
                return True  # Explicitamente retorna True em caso de sucesso
        except Exception as err:
            self.logger.error(err)
            self.connection.rollback()
            self._exception = err
            updated = False
        finally:
            self._close()

        # Retorna False em caso de erro
        return updated

    def get(self, value, key=None, where: dict = None, fields: list = None):
        """
        Obtém um registro de empresa no banco de dados.

        Este método consulta a tabela de empresas e retorna um registro específico baseado no valor
        de uma chave e nos filtros fornecidos, se houver.

        Args:
            value (Any): Valor da chave de busca para localizar o registro.
            key (str, optional): Nome do campo utilizado como chave para a consulta. Caso não seja
            informado, será utilizada a chave primária (`PK`).
            where (dict, optional): Dicionário de condições adicionais para a cláusula WHERE.
            fields (list, optional): Lista de campos específicos a serem retornados.
            Se não informado, todos os campos são retornados.

        Returns:
            CompanyVO | None: Retorna um objeto `CompanyVO` com os dados da empresa se encontrado,
                               ou `None` se não encontrado ou em caso de erro.

        Raises:
            Exception: Captura e registra qualquer erro ocorrido durante a consulta.
        """
        key_type = '%s'
        if key is None:
            key = self.PK

        if where is None:
            where = dict()

        if fields is None or len(fields) == 0:
            fields = '*'
        else:
            fields = [self.BASE_TABLE_ALIAS + '.' + val for val in fields]
            fields = ",".join(fields)

        sql = "SELECT {} FROM {} as {} WHERE {} = {}".format(
            fields, self.BASE_TABLE, self.BASE_TABLE_ALIAS, key, key_type)

        if where != dict():
            where_str = self.build_where(where)
            sql = sql + " WHERE {}".format(where_str)

        try:
            result = self._execute(sql, value)
            item = result.fetchone()

            if item:
                item = CompanyVO(**item)

        except Exception as err:
            self.logger.error(err)
            item = None
        finally:
            self._close()

        return item

    def list(self, where: dict, offset=None, limit=None, fields: list = None, sort_by=None,
             order_by=None):
        """
        Lista registros de empresas no banco de dados com filtros, ordenação e paginação.

        Este método consulta a tabela de empresas, aplicando filtros, ordenação e
        limites de resultados.

        Args:
            where (dict): Dicionário de condições adicionais para a cláusula WHERE.
            offset (int, optional): Número de registros a serem ignorados antes de
            iniciar a consulta (paginação).
            limit (int, optional): Número máximo de registros a serem retornados.
            fields (list, optional): Lista de campos específicos a serem retornados.
            Se não informado, todos os campos são retornados.
            sort_by (str | list, optional): Campo(s) para ordenar os resultados.
            Se não informado, será utilizado a chave primária.
            order_by (str, optional): Direção da ordenação, pode ser "ASC" ou "DESC". O padrão "ASC"

        Returns:
            list: Retorna uma lista de dicionários contendo os registros encontrados,
                  ou `None` em caso de erro ou se nenhum registro for encontrado.

        Raises:
            Exception: Captura e registra qualquer erro ocorrido durante a consulta.
        """
        if fields is None or len(fields) == 0:
            fields = '*'
        else:
            fields = [self.BASE_TABLE_ALIAS + '.' + val for val in fields]
            fields = ",".join(fields)

        if order_by is None:
            order_by = Order.ASC

        if sort_by is None:
            sort_by = self.PK
        elif isinstance(sort_by, list):
            sort_by_arr = [self.BASE_TABLE_ALIAS + '.' + val for val in sort_by]
            sort_by = ",".join(sort_by_arr)
        else:
            sort_by = self.BASE_TABLE_ALIAS + '.' + sort_by

        sql = "SELECT {} FROM {} as {}".format(fields, self.BASE_TABLE, self.BASE_TABLE_ALIAS)

        if where != dict():
            where_str = self.build_where(where)
            sql = sql + " WHERE {}".format(where_str)

        sql = sql + " ORDER BY {} {}".format(sort_by, order_by)

        if not offset:
            offset = Pagination.validate(PaginationType.OFFSET, offset)

        if not limit:
            limit = Pagination.validate(PaginationType.LIMIT, limit)

        sql = sql + " LIMIT {},{}".format(offset, limit)

        try:
            result = self._execute(sql)
            result = result.fetchall()
        except Exception as err:
            self.logger.error(err)
            self._exception = err
            result = None
        finally:
            self._close()

        return result

    def build_where(self, where):
        """
        Constrói a cláusula WHERE para a consulta SQL com base nas condições fornecidas.

        Este método recebe um dicionário de condições e constrói a parte WHERE da query,
        considerando se o valor é `None` ou um valor específico.

        Args:
            where (dict): Dicionário de condições para a cláusula WHERE. As chaves são os
            campos da tabela e os valores são os valores pelos quais os campos serão filtrados.

        Returns:
            str: Retorna a string da cláusula WHERE gerada, com as condições aplicadas.

        Example:
            where = {'id': 1, 'name': 'Company X'}
            build_where(where)
            'c.id = 1 AND c.name = "Company X"'

            where = {'id': None}
            build_where(where)
            'c.id IS NULL'
        """
        where_list = []
        for k_key, val in where.items():
            if val is None:
                where_value = '{} IS NULL'.format(self.BASE_TABLE_ALIAS + "." + k_key)
            else:
                where_value = '{} = {}'.format(self.BASE_TABLE_ALIAS + "." + k_key,
                                               '"{}"'.format(val) if isinstance(val, str) else val)
            where_list.append(where_value)
        where_str = " AND ".join(where_list)
        return where_str

    def count(self, where: dict, sort_by=None, order_by=None):
        """
        Conta o número total de registros na tabela com base nas condições fornecidas.

        Este método constrói e executa uma consulta SQL para contar o número de registros
        na tabela, aplicando as condições de filtro (WHERE), ordenação (ORDER BY) e outras
        opções fornecidas.

        Args:
            where (dict): Dicionário de condições para a cláusula WHERE. As chaves são os
            campos da tabela e os valores são os valores pelos quais os campos serão filtrados.
            sort_by (str | list, opcional): Campo(s) para ordenar os resultados
            (padrão é a chave primária).
            order_by (str, opcional): Direção de ordenação, podendo ser 'ASC' ou 'DESC'
            (padrão é 'ASC').

        Returns:
            int: O número total de registros que atendem às condições fornecidas.

        Example:
            where = {'status': 'active'}
            count(where)
            10
        """
        if order_by is None:
            order_by = Order.ASC

        if sort_by is None:
            sort_by = self.PK
        elif isinstance(sort_by, list):
            sort_by_arr = [self.BASE_TABLE_ALIAS + '.' + val for val in sort_by]
            sort_by = ",".join(sort_by_arr)
        else:
            sort_by = self.BASE_TABLE_ALIAS + '.' + sort_by

        sql = "SELECT COUNT(1) as total FROM {} as {}".format(self.BASE_TABLE,
                                                              self.BASE_TABLE_ALIAS)

        if where != dict():
            where_str = self.build_where(where)
            sql = sql + " WHERE {}".format(where_str)

        sql = sql + " ORDER BY {} {}".format(sort_by, order_by)

        try:
            result = self._execute(sql)
            result = result.fetchone()
            result = result['total']
        except Exception as err:
            self.logger.error(err)
            self._exception = err
            result = 0
        finally:
            self._close()

        return result

    def soft_delete(self, value, key=None):
        """
        Executa uma exclusão suave (soft delete) no registro especificado, definindo
        o campo `deleted_at`.

        Este método marca o registro com o valor de `deleted_at` para indicar que ele foi removido,
        sem excluir fisicamente os dados do banco de dados. O valor de `deleted_at` é atualizado com
        a data e hora atual.

        Args:
            value (str | int): O valor da chave primária do registro a ser excluído suavemente.
            key (str, opcional): O nome do campo utilizado como chave para identificar o registro
            (padrão é a chave primária).

        Returns:
            bool: Retorna True se a operação foi bem-sucedida, False caso contrário.

        Example:
            soft_delete(123)
            True
        """
        key_type = '%s'
        if key is None:
            key = self.PK

        sql = "UPDATE {}.{} SET deleted_at = %s WHERE {} = {}".format(
            self.BASE_SCHEMA, self.BASE_TABLE, key, key_type)

        data = (datetime.today(), value,)
        try:
            result = self._execute(sql, data)
            self.connection.commit()
        except Exception as err:
            self.logger.error("SQL: {} ".format(sql))
            self.logger.error("Params: {} ".format(data))
            self.logger.error(err)
            result = None
            self.connection.rollback()
        finally:
            self._close()

        return result
