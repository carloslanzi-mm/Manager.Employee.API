import unittest
from unittest.mock import MagicMock
from unittest_data_provider import data_provider

from flambda_app.database.mysql import MySQLConnector
from flambda_app.request_control import Pagination, Order
from flambda_app.logging import get_logger
from flambda_app.repositories.v1.mysql.employee_respository import EmployeeRepository
from flambda_app.vos.employee import EmployeeVO
from tests.component.componenttestutils import BaseComponentTestCase
from tests.unit.helpers.employee_helper import get_employee_sample
from tests.unit.testutils import get_function_name

def get_employee():
    employee_dict = get_employee_sample()
    employee_dict["id"] = None
    employee = EmployeeVO(employee_dict)
    return (employee,),

def get_list_data():
    where = dict()
    offset = Pagination.OFFSET
    limit = Pagination.LIMIT
    fields = []
    sort_by = None
    order_by = None
    
    return (
        (where, offset, limit, fields, sort_by, order_by),
        (where, offset, limit, ['id', 'name'], sort_by, order_by),
        (where, offset, limit, ['id', 'name'], sort_by, Order.DESC),
        ({'uuid': '123e4567-e89b-12d3-a456-426614174000'}, offset, limit, ['id', 'name'], sort_by, Order.DESC),
    )

class EmployeeRepositoryTestCase(BaseComponentTestCase):
    
    @classmethod
    def setUpClass(cls):
        BaseComponentTestCase.setUpClass()
        cls.logger = get_logger()
    
    def setUp(self):
        super().setUp()
        
        # Mock da conexão MySQL com os métodos necessários
        self.connection = MagicMock()
        self.connection.insert_id = MagicMock(return_value=1)
        self.connection.commit = MagicMock()
        self.connection.rollback = MagicMock()
        self.connection.close = MagicMock()
        
        self.repository = EmployeeRepository(logger=self.logger, mysql_connection=self.connection)
        self.repository.debug = True
    
    @data_provider(get_employee)
    def test_create(self, employee: EmployeeVO):
        self.logger.info('Running test: %s', get_function_name(__name__))
        self.repository._execute = MagicMock(return_value=True)
        
        result = self.repository.create(employee)
        self.assertTrue(result)
        self.logger.info('Employee created: {}'.format(employee.id))
    
    @data_provider(get_employee)
    def test_get(self, employee: EmployeeVO):
        self.logger.info('Running test: %s', get_function_name(__name__))
        employee.uuid = "123e4567-e89b-12d3-a456-426614174000"
        self.repository._execute = MagicMock()
        self.repository._execute().fetchone.return_value = employee.to_dict()
        
        response = self.repository.get(employee.id)
        self.assertIsNotNone(response)
        
        response = self.repository.get(employee.uuid, key='uuid')
        self.assertIsNotNone(response)
    
    @data_provider(get_list_data)
    def test_list(self, where, offset, limit, fields, sort_by, order_by):
        self.logger.info('Running test: %s', get_function_name(__name__))
        self.repository._execute = MagicMock()
        self.repository._execute().fetchall.return_value = [{"id": 1, "name": "Employee A"}]
        
        result = self.repository.list(where, offset, limit, fields, sort_by, order_by)
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 0)
    
    @data_provider(get_list_data)
    def test_count(self, where, offset, limit, fields, sort_by, order_by):
        self.logger.info('Running test: %s', get_function_name(__name__))
        self.repository._execute = MagicMock()
        self.repository._execute().fetchone.return_value = {'total': 5}
        
        result = self.repository.count(where, sort_by, order_by)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, int)
        self.assertEqual(result, 5)
    
    @data_provider(get_employee)
    def test_update(self, employee: EmployeeVO):
        self.logger.info('Running test: %s', get_function_name(__name__))
        self.repository._execute = MagicMock(return_value=True)
        
        result = self.repository.update(employee, employee.id)
        self.assertTrue(result)
    
    @data_provider(get_employee)
    def test_soft_delete(self, employee: EmployeeVO):
        self.logger.info('Running test: %s', get_function_name(__name__))
        self.repository._execute = MagicMock(return_value=True)
        
        result = self.repository.soft_delete(employee.id)
        self.assertTrue(result)
        
if __name__ == '__main__':
    unittest.main()
