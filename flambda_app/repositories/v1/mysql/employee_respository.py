from datetime import datetime
from flambda_app.request_control import Order, Pagination, PaginationType
from flambda_app.repositories.v1.mysql import AbstractRepository
from flambda_app.vos.employee import EmployeeVO


class EmployeeRepository(AbstractRepository):
    BASE_TABLE = 'employee'
    BASE_SCHEMA = 'store'
    BASE_TABLE_ALIAS = 'e'
    PK = 'id'
    UUID_KEY = 'uuid'

    def __init__(self, logger=None, mysql_connection=None):
        super().__init__(logger, mysql_connection)

    def create(self, employee: EmployeeVO) -> bool:
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
            created = self._execute(sql, values)
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
        for k, v in employee.to_dict().items():
            if k in keys:
                update_data.append('{}.{}=%s'.format(self.BASE_TABLE_ALIAS, k))
                values.append(v)

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
        key_type = '%s'
        if key is None:
            key = self.PK

        if where is None:
            where = dict()

        if fields is None or len(fields) == 0:
            fields = '*'
        else:
            fields = [self.BASE_TABLE_ALIAS + '.' + v for v in fields]
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
        if fields is None or len(fields) == 0:
            fields = '*'
        else:
            fields = [self.BASE_TABLE_ALIAS + '.' + v for v in fields]
            fields = ",".join(fields)

        if order_by is None:
            order_by = Order.ASC

        if sort_by is None:
            sort_by = self.PK
        elif isinstance(sort_by, list):
            sort_by_arr = [self.BASE_TABLE_ALIAS + '.' + v for v in sort_by]
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
        where_list = []
        for k, v in where.items():
            if v is None:
                where_value = '{} IS NULL'.format(self.BASE_TABLE_ALIAS + "." + k)
            else:
                where_value = '{} = {}'.format(self.BASE_TABLE_ALIAS + "." + k,
                                               '"{}"'.format(v) if isinstance(v, str) else v)
            where_list.append(where_value)
        where_str = " AND ".join(where_list)
        return where_str

    def count(self, where: dict, sort_by=None, order_by=None):
        if order_by is None:
            order_by = Order.ASC

        if sort_by is None:
            sort_by = self.PK
        elif isinstance(sort_by, list):
            sort_by_arr = [self.BASE_TABLE_ALIAS + '.' + v for v in sort_by]
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
