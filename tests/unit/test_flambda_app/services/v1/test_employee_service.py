import unittest
from unittest.mock import MagicMock

from flambda_app.logging import get_logger
from flambda_app.services.v1.employee_service import EmployeeService
from flambda_app.repositories.v1.mysql.employee_respository import EmployeeRepository
from flambda_app.vos.employee import EmployeeVO
from flambda_app.enums.messages import MessagesEnum
from flambda_app.exceptions import DatabaseException, ValidationException
from tests.unit.testutils import get_function_name

class EmployeeServiceTestCase(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.logger = get_logger()
    
    def setUp(self):
        super().setUp()
        
        # Mock do EmployeeRepository
        self.employee_repository = MagicMock(spec=EmployeeRepository)
        self.employee_repository.get_exception.return_value = None  # Garante que não há exceção
        
        self.service = EmployeeService(logger=self.logger, employee_repository=self.employee_repository)
    
    def test_list(self):
        self.logger.info('Running test: %s', get_function_name(__name__))
        employee = EmployeeVO({"id": 1, "name": "Employee A"})
        self.employee_repository.list.return_value = [employee.to_dict()]
        
        request = {"where": {}, "offset": 0, "limit": 10, "order_by": "id", "sort_by": "asc", "fields": ["id", "name"]}
        result = self.service.list(request)
        
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 0)
        self.assertEqual(result[0]['id'], 1)
    
    def test_count(self):
        self.logger.info('Running test: %s', get_function_name(__name__))
        self.employee_repository.count.return_value = 5
        
        request = {"where": {}, "order_by": "id", "sort_by": "asc"}
        result = self.service.count(request)
        
        self.assertIsInstance(result, int)
        self.assertEqual(result, 5)
    
    def test_get(self):
        self.logger.info('Running test: %s', get_function_name(__name__))
        employee = EmployeeVO({"id": 1, "name": "Employee A"})
        self.employee_repository.get.return_value = employee.to_dict()
        
        request = {"where": {}, "fields": ["id", "name"]}
        result = self.service.get(request, 1)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['id'], 1)
    
    def test_create(self):
        self.logger.info('Running test: %s', get_function_name(__name__))
        self.employee_repository.create.return_value = True
        
        request = {"where": {"name": "Employee A"}}
        result = self.service.create(request)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], "Employee A")
    
    def test_update(self):
        self.logger.info('Running test: %s', get_function_name(__name__))
        employee = EmployeeVO({"id": 1, "name": "Employee A"})
        self.employee_repository.get.return_value = employee
        self.employee_repository.update.return_value = True
        
        request = {"where": {"name": "Employee Updated"}}
        result = self.service.update(request, "uuid-1234")
        
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], "Employee Updated")
    
    def test_delete(self):
        self.logger.info('Running test: %s', get_function_name(__name__))
        self.employee_repository.get.return_value = EmployeeVO({"id": 1, "name": "Employee A"})
        self.employee_repository.soft_delete.return_value = True
        
        request = {"where": {}}
        result = self.service.delete(request, "uuid-1234")
        
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()