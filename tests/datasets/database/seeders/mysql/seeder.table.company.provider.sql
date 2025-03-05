INSERT INTO employee (uuid, company_id, name, hourly_rate, is_admin, is_active, created_at, updated_at)
VALUES
  (UUID(), 1, 'João da Silva', 50.00, FALSE, TRUE, NOW(), NOW()),  -- Exemplo de prestador sem admin
  (UUID(), 1, 'Maria Oliveira', 70.00, TRUE, TRUE, NOW(), NOW()),  -- Exemplo de prestador admin
  (UUID(), 2, 'Carlos Pereira', 45.00, FALSE, TRUE, NOW(), NOW()),  -- Outro prestador
  (UUID(), 2, 'Ana Souza', 60.00, FALSE, FALSE, NOW(), NOW());    -- Prestador inativo

-- Exemplo de prestador deletado:
INSERT INTO employee (uuid, company_id, name, hourly_rate, is_admin, is_active, created_at, updated_at, deleted_at)
VALUES
  (UUID(), 3, 'Ricardo Lima', 55.00, FALSE, FALSE, NOW(), NOW(), NOW());
