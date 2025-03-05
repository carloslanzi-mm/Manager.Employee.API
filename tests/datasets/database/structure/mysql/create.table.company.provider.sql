CREATE TABLE employee (
    id INT AUTO_INCREMENT PRIMARY KEY,  -- Chave primária auto-increment
    uuid VARCHAR(60) NOT NULL, -- Gerando o UUID automaticamente
    company_id INT,  -- FK para a tabela company
    name VARCHAR(255) NOT NULL,  -- Nome do prestador
    hourly_rate DECIMAL(10, 2),  -- Valor por hora
    is_admin BOOLEAN DEFAULT FALSE,  -- Indica se o prestador é administrador
    is_active BOOLEAN DEFAULT TRUE,  -- Indica se o prestador está ativo
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Data de criação
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,  -- Data de atualização
    deleted_at TIMESTAMP NULL,  -- Data de exclusão (para soft delete)
    CONSTRAINT fk_company
        FOREIGN KEY (company_id)
        REFERENCES company(id)  -- Referência à tabela company pela coluna 'id'
        ON DELETE SET NULL  -- Quando uma empresa for excluída, o campo company_id será setado como NULL
);
