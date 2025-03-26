"""
Módulo responsável por gerenciar operações relacionadas ao funcionario.
"""

from datetime import datetime
from flambda_app.request_control import Order, Pagination, PaginationType
from flambda_app.repositories.v1.mysql import AbstractRepository
from flambda_app.vos.employee import EmployeeVO


class EmployeeRepository(AbstractRepository):
    """Repository class for managing Employee data.

    Attributes:
        BASE_TABLE (str): The name of the employee table.
        BASE_SCHEMA (str): The database schema where the table is located.
        BASE_TABLE_ALIAS (str): The alias used for the employee table in queries.
        PK (str): The primary key column of the employee table.
        UUID_KEY (str): The UUID key column of the employee table.
    """
    BASE_TABLE = 'employee'
    BASE_SCHEMA = 'store'
    BASE_TABLE_ALIAS = 'e'
    PK = 'id'
    UUID_KEY = 'uuid'

    def __init__(self, logger=None, mysql_connection=None):
        """Initializes the EmployeeRepository.

        Args:
            logger (optional): Logger instance for logging messages. Defaults to None.
            mysql_connection (optional): MySQL connection instance for database operations.
            Defaults to None.
        """
        super().__init__(logger, mysql_connection)

    def create(self, employee: EmployeeVO) -> bool:
        """Inserts a new employee record into the database.

        Args:
            employee (EmployeeVO): The employee data to insert.

        Returns:
            bool: True if the record was successfully inserted, otherwise False.
        """
        keys = list(employee.to_dict().keys())
        # Remover a PK
        keys.remove(self.PK)
        keys_str = ",".join(keys)
        values_count = len(employee.to_dict().values()) - 1  # Excluindo a PK
        values_str = ",".join(['%s' for _ in range(values_count)])

        # Query
        sql = "INSERT INTO {} ({}) VALUES ({})".format(self.BASE_TABLE, keys_str, values_str)

        # Tratamentos finais
        employee_dict = employee.to_dict()
        del employee_dict[self.PK]
        values = tuple(employee_dict.values())

        # Tentando criar
        try:
            self._execute(sql, values)
            # Pegando o último id inserido
            employee.id = self.connection.insert_id()
            # Commit
            self.connection.commit()

            # Em caso de sucesso, retorne True
            created = True

        except Exception as err:
            self.logger.error(err)
            self.connection.rollback()
            self._exception = err
            created = False

        finally:
            self._close()

        # Retorne False apenas em caso de falha
        return created

    def update(self, employee: EmployeeVO, value, key=None):
        """Updates an existing employee record in the database.

        Args:
            employee (EmployeeVO): The employee data to update.
            value: The value of the key used to identify the record.
            key (str, optional): The column name to filter the update. Defaults to the primary key.

        Returns:
            bool: True if the record was successfully updated, otherwise False.
        """
        key_type = '%s'
        if key is None:
            key = self.PK

        keys = list(employee.to_dict().keys())
        # Remover a PK
        keys.remove(self.PK)
        # Remover o UUID
        keys.remove(self.UUID_KEY)

        # Preparando os valores
        values = []
        update_data = []
        for k_key, v_value in employee.to_dict().items():
            if k_key in keys:
                update_data.append('{}.{}=%s'.format(self.BASE_TABLE_ALIAS, k_key))
                values.append(v_value)

        update_str = ",".join(update_data)
        # Query
        sql = "UPDATE {} as {} SET {} WHERE {}.{} = {}".format(self.BASE_TABLE,
                                                               self.BASE_TABLE_ALIAS, update_str,
                                                               self.BASE_TABLE_ALIAS, key, key_type)

        # Tratamentos finais
        employee_dict = employee.to_dict()
        del employee_dict[self.PK]
        del employee_dict[self.UUID_KEY]
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
        """Retrieves an employee record from the database based on specified conditions.

        Args:
            value: The value of the key used to filter the record.
            key (str, optional): The column name to filter the query. Defaults to the primary key.
            where (dict, optional): Additional conditions to filter the query. Defaults to None.
            fields (list, optional): Specific fields to retrieve. Defaults to all fields ('*').

        Returns:
            EmployeeVO or None: The employee record as an EmployeeVO
            object if found, otherwise None.
        """
        key_type = '%s'
        if key is None:
            key = self.PK

        if where is None:
            where = dict()

        if fields is None or len(fields) == 0:
            fields = '*'
        else:
            fields = [self.BASE_TABLE_ALIAS + '.' + v_value for v_value in fields]
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
                item = EmployeeVO(**item)

        except Exception as err:
            self.logger.error(err)
            item = None
        finally:
            self._close()

        return item

    def list(self, where: dict, offset=None, limit=None, fields: list = None, sort_by=None,
             order_by=None):
        """Retrieves a list of employee records from the database with optional filtering, sorting,
        and pagination.

        Args:
            where (dict): Conditions to filter the query results.
            offset (int, optional): The starting point for pagination. Defaults to None.
            limit (int, optional): The maximum number of records to retrieve. Defaults to None.
            fields (list, optional): Specific fields to retrieve. Defaults to all fields ('*').
            sort_by (str or list, optional): The field(s) to sort the results by.
            Defaults to the primary key.
            order_by (str, optional): The sort order ('ASC' or 'DESC'). Defaults to 'ASC'.

        Returns:
            list: A list of employee records (or an empty list if no records found).
        """
        if fields is None or len(fields) == 0:
            fields = '*'
        else:
            fields = [self.BASE_TABLE_ALIAS + '.' + v_value for v_value in fields]
            fields = ",".join(fields)

        if order_by is None:
            order_by = Order.ASC

        if sort_by is None:
            sort_by = self.PK
        elif isinstance(sort_by, list):
            sort_by_arr = [self.BASE_TABLE_ALIAS + '.' + v_value for v_value in sort_by]
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
        """Builds a WHERE clause for SQL queries based on the provided conditions.

        Args:
            where (dict): A dictionary where keys are column names and values are the conditions.

        Returns:
            str: The WHERE clause as a string, formatted with proper SQL syntax.
        """
        where_list = []
        for k_key, v_value in where.items():
            if v_value is None:
                where_value = '{} IS NULL'.format(self.BASE_TABLE_ALIAS + "." + k_key)
            else:
                where_value = '{} = {}'.format(self.BASE_TABLE_ALIAS + "." + k_key,
                                               '"{}"'.format(v_value) if isinstance(v_value, str)
                                               else v_value)
            where_list.append(where_value)
        where_str = " AND ".join(where_list)
        return where_str

    def count(self, where: dict, sort_by=None, order_by=None):
        """Counts the number of employee records in the database based on specified conditions.

        Args:
            where (dict): Conditions to filter the query results.
            sort_by (str or list, optional): The field(s) to sort the results by.
            Defaults to the primary key.
            order_by (str, optional): The sort order ('ASC' or 'DESC'). Defaults to 'ASC'.

        Returns:
            int: The total number of records that match the specified conditions.
        """
        if order_by is None:
            order_by = Order.ASC

        if sort_by is None:
            sort_by = self.PK
        elif isinstance(sort_by, list):
            sort_by_arr = [self.BASE_TABLE_ALIAS + '.' + v_value for v_value in sort_by]
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
        """Marks an employee record as deleted by setting the 'deleted_at' timestamp.

        Args:
            value: The value of the key used to identify the record to be deleted.
            key (str, optional): The column name to filter the update. Defaults to the primary key.

        Returns:
            bool: True if the record was successfully marked as deleted, otherwise False.
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
