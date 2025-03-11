import unittest
from unittest.mock import MagicMock

from flambda_app.logging import get_logger
from flambda_app.services.company_manager import CompanyManager
from flambda_app.services.v1.company_service import CompanyService
from tests.unit.testutils import get_function_name

class CompanyManagerTestCase(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.logger = get_logger()
    
    def setUp(self):
        super().setUp()
        
        # Mock do CompanyService
        self.company_service = MagicMock(spec=CompanyService)
        self.company_service.exception = None  # Garante que o mock tenha o atributo exception
        
        self.manager = CompanyManager(logger=self.logger, company_service=self.company_service)
    
    def test_list(self):
        self.logger.info('Running test: %s', get_function_name(__name__))
        self.company_service.list.return_value = [{"id": 1, "name": "Company A"}]
        
        result = self.manager.list({})
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 0)
    
    def test_count(self):
        self.logger.info('Running test: %s', get_function_name(__name__))
        self.company_service.count.return_value = 5
        
        result = self.manager.count({})
        self.assertIsInstance(result, int)
        self.assertEqual(result, 5)
    
    def test_get(self):
        self.logger.info('Running test: %s', get_function_name(__name__))
        self.company_service.get.return_value = {"id": 1, "name": "Company A"}
        
        result = self.manager.get({}, 1)
        self.assertIsNotNone(result)
    
    def test_create(self):
        self.logger.info('Running test: %s', get_function_name(__name__))
        self.company_service.create.return_value = {"id": 1, "name": "Company A"}
        
        result = self.manager.create({})
        self.assertIsNotNone(result)
    
    def test_update(self):
        self.logger.info('Running test: %s', get_function_name(__name__))
        self.company_service.update.return_value = {"id": 1, "name": "Company Updated"}
        
        result = self.manager.update({}, "uuid-1234")
        self.assertIsNotNone(result)
    
    def test_delete(self):
        self.logger.info('Running test: %s', get_function_name(__name__))
        self.company_service.delete.return_value = True
        
        result = self.manager.delete({}, "uuid-1234")
        self.assertTrue(result)
        
if __name__ == '__main__':
    unittest.main()