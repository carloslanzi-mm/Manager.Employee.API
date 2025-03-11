import unittest
from unittest.mock import MagicMock

from flambda_app.logging import get_logger
from flambda_app.services.employee_manager import EmployeeManager
from flambda_app.services.v1.employee_service import EmployeeService
from flambda_app.vos.employee import EmployeeVO
from tests.unit.testutils import get_function_name

class EmployeeManagerTestCase(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.logger = get_logger()
    
    def setUp(self):
        super().setUp()
        
        # Mock do EmployeeService
        self.employee_service = MagicMock(spec=EmployeeService)
        self.employee_service.exception = None  # Garante que o mock tenha o atributo exception
        
        self.manager = EmployeeManager(logger=self.logger, employee_service=self.employee_service)
    
    def test_list(self):
        self.logger.info('Running test: %s', get_function_name(__name__))
        employee = EmployeeVO({"id": 1, "name": "Employee A"})
        self.employee_service.list.return_value = [employee]
        
        result = self.manager.list({})
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 0)
        self.assertIsInstance(result[0], EmployeeVO)
    
    def test_count(self):
        self.logger.info('Running test: %s', get_function_name(__name__))
        self.employee_service.count.return_value = 5
        
        result = self.manager.count({})
        self.assertIsInstance(result, int)
        self.assertEqual(result, 5)
    
    def test_get(self):
        self.logger.info('Running test: %s', get_function_name(__name__))
        employee = EmployeeVO({"id": 1, "name": "Employee A"})
        self.employee_service.get.return_value = employee
        
        result = self.manager.get({}, 1)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, EmployeeVO)
    
    def test_create(self):
        self.logger.info('Running test: %s', get_function_name(__name__))
        employee = EmployeeVO({"id": 1, "name": "Employee A"})
        self.employee_service.create.return_value = employee
        
        result = self.manager.create({})
        self.assertIsNotNone(result)
        self.assertIsInstance(result, EmployeeVO)
    
    def test_update(self):
        self.logger.info('Running test: %s', get_function_name(__name__))
        employee = EmployeeVO({"id": 1, "name": "Employee Updated"})
        self.employee_service.update.return_value = employee
        
        result = self.manager.update({}, "uuid-1234")
        self.assertIsNotNone(result)
        self.assertIsInstance(result, EmployeeVO)
    
    def test_delete(self):
        self.logger.info('Running test: %s', get_function_name(__name__))
        self.employee_service.delete.return_value = True
        
        result = self.manager.delete({}, "uuid-1234")
        self.assertTrue(result)
        
if __name__ == '__main__':
    unittest.main()