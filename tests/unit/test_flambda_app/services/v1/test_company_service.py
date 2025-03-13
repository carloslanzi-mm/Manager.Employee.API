import unittest
from unittest.mock import MagicMock

from flambda_app.logging import get_logger
from flambda_app.services.v1.company_service import CompanyService
from flambda_app.repositories.v1.mysql.company_repository import CompanyRepository
from flambda_app.vos.company import CompanyVO
from flambda_app.enums.messages import MessagesEnum
from flambda_app.exceptions import DatabaseException, ValidationException
from tests.unit.testutils import get_function_name

class CompanyServiceTestCase(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.logger = get_logger()
    
    def setUp(self):
        super().setUp()
        
        # Mock do CompanyRepository
        self.company_repository = MagicMock(spec=CompanyRepository)
        self.company_repository.get_exception.return_value = None  # Garante que não há exceção
        
        self.service = CompanyService(logger=self.logger, company_repository=self.company_repository)
    
    def test_list(self):
        self.logger.info('Running test: %s', get_function_name(__name__))
        company = CompanyVO({"id": 1, "name": "Company A"})
        self.company_repository.list.return_value = [company.to_dict()]
        
        request = {"where": {}, "offset": 0, "limit": 10, "order_by": "id", "sort_by": "asc", "fields": ["id", "name"]}
        result = self.service.list(request)
        
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 0)
        self.assertEqual(result[0]['id'], 1)
    
    def test_count(self):
        self.logger.info('Running test: %s', get_function_name(__name__))
        self.company_repository.count.return_value = 5
        
        request = {"where": {}, "order_by": "id", "sort_by": "asc"}
        result = self.service.count(request)
        
        self.assertIsInstance(result, int)
        self.assertEqual(result, 5)
    
    def test_get(self):
        self.logger.info('Running test: %s', get_function_name(__name__))
        company = CompanyVO({"id": 1, "name": "Company A"})
        self.company_repository.get.return_value = company.to_dict()
        
        request = {"where": {}, "fields": ["id", "name"]}
        result = self.service.get(request, 1)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['id'], 1)
    
    def test_create(self):
        self.logger.info('Running test: %s', get_function_name(__name__))
        self.company_repository.create.return_value = True
        
        request = {"where": {"name": "Company A"}}
        result = self.service.create(request)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], "Company A")
    
    def test_update(self):
        self.logger.info('Running test: %s', get_function_name(__name__))
        company = CompanyVO({"id": 1, "name": "Company A"})
        self.company_repository.get.return_value = company
        self.company_repository.update.return_value = True
        
        request = {"where": {"name": "Company Updated"}}
        result = self.service.update(request, "uuid-1234")
        
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], "Company Updated")
    
    def test_delete(self):
        self.logger.info('Running test: %s', get_function_name(__name__))
        self.company_repository.get.return_value = CompanyVO({"id": 1, "name": "Company A"})
        self.company_repository.soft_delete.return_value = True
        
        request = {"where": {}}
        result = self.service.delete(request, "uuid-1234")
        
        self.assertTrue(result)
        
if __name__ == '__main__':
    unittest.main()
