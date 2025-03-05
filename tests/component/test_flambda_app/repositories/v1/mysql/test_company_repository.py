import pytest
from unittest.mock import MagicMock
from datetime import datetime
from flambda_app.repositories.v1.mysql.company_repository import CompanyRepository
from flambda_app.vos.company import CompanyVO


@pytest.fixture
def mock_db():
    """Fixture para mockar a conexão com o banco de dados."""
    mock_connection = MagicMock()
    return mock_connection


@pytest.fixture
def company_repository(mock_db):
    """Fixture para criar uma instância do repositório com a conexão mockada."""
    return CompanyRepository(mysql_connection=mock_db)


def test_create_company(company_repository, mock_db):
    """Testa a criação de uma nova empresa no banco de dados."""

    # Cria um objeto CompanyVO com dados fictícios
    company_vo = CompanyVO(data={
        'id': None,
        'uuid': '123e4567-e89b-12d3-a456-426614174000',
        'name': 'Test Company',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'deleted_at': None
    })

    # Mock do retorno da inserção, simulando que a inserção é bem-sucedida
    mock_db.execute.return_value = None  # Simula um comando SQL sem retorno
    mock_db.insert_id.return_value = 1  # Simula que o ID do último inserido é 1

    # Chama o método create do repositório
    result = company_repository.create(company_vo)

    # Verifica se o resultado é True, o que indica que a criação foi bem-sucedida
    assert result is True  # O resultado deve ser True, indicando sucesso

    # Verifica se o commit foi chamado
    mock_db.commit.assert_called_once()

    # Verifica se o ID da empresa foi atualizado para 1
    assert company_vo.id == 1

    # Verifica se a execução do método `execute` foi chamada
    mock_db.execute.assert_called_once()  # Verifica se o comando execute foi chamado


def test_update_company(company_repository, mock_db):
    """Testa a atualização de uma empresa no banco de dados."""

    # Cria um objeto CompanyVO com dados fictícios
    company_vo = CompanyVO(data={
        'id': 1,
        'uuid': '123e4567-e89b-12d3-a456-426614174000',
        'name': 'Updated Company',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'deleted_at': None
    })

    # Mock do retorno da execução do update
    mock_db._execute.return_value = True

    # Chama o método update do repositório
    result = company_repository.update(company_vo, 1)

    # Verifica se o método de execução foi chamado corretamente
    assert result is True
    mock_db.commit.assert_called_once()  # Verifica se o commit foi chamado


# def test_get_company(company_repository, mock_db):
#     """Testa a busca de uma empresa no banco de dados."""
#
#     # Mock do retorno do banco de dados
#     mock_cursor = mock_db._execute.return_value
#     mock_cursor.fetchone.return_value = {
#         'id': 1,
#         'uuid': '123e4567-e89b-12d3-a456-426614174000',
#         'name': 'Test Company',
#         'created_at': datetime.now().isoformat(),
#         'updated_at': datetime.now().isoformat(),
#         'deleted_at': None
#     }
#
#     # Criando o objeto CompanyVO com o mock para 'name'
#     company_object = MagicMock(spec=CompanyVO)
#     company_object.name = 'Test Company'  # Atribuindo o valor real para 'name'
#     company_object.id = 1
#     company_object.uuid = '123e4567-e89b-12d3-a456-426614174000'
#
#     # Configure o mock para retornar o objeto mockado de CompanyVO
#     mock_cursor.fetchone.return_value = company_object
#
#     # Chama o método get do repositório
#     result = company_repository.get(1)
#
#     # Verifique o tipo de result
#     print(f"result type: {type(result)}")
#     print(f"result: {result}")
#
#     # Verifica se o retorno não é None
#     assert result is not None
#
#     # Verifica se o resultado é uma instância de CompanyVO
#     assert isinstance(result, CompanyVO)


# def test_list_companies(company_repository, mock_db):
#     """Testa a listagem de empresas no banco de dados."""
#
#     # Mock do retorno do banco de dados
#     mock_cursor = mock_db._execute.return_value
#     mock_cursor.fetchall.return_value = [
#         {'id': 1, 'uuid': '123e4567-e89b-12d3-a456-426614174000', 'name': 'Company 1',
#          'created_at': datetime.now().isoformat()},
#         {'id': 2, 'uuid': '223e4567-e89b-12d3-a456-426614174000', 'name': 'Company 2',
#          'created_at': datetime.now().isoformat()}
#     ]
#
#     # Mock do cursor para garantir que a chamada fetchall() retorne o valor correto
#     mock_db._execute.return_value = mock_cursor
#
#     # Chama o método list do repositório
#     result = company_repository.list(where={})
#
#     # Verifica se o resultado contém as empresas esperadas
#     assert len(result) == 2
#     assert result[0]['name'] == 'Company 1'
#     assert result[1]['name'] == 'Company 2'


# def test_soft_delete_company(company_repository, mock_db):
#     """Testa a exclusão lógica de uma empresa no banco de dados."""
#
#     # Mock do retorno da execução do soft delete
#     mock_db._execute.return_value = True
#
#     # Chama o método soft_delete do repositório
#     result = company_repository.soft_delete(1)
#
#     # Verifica se o método de execução foi chamado corretamente
#     assert result is True
#     mock_db.commit.assert_called_once()  # Verifica se o commit foi chamado
