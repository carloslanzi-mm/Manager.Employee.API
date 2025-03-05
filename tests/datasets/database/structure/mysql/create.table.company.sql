CREATE TABLE company (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(60) NOT NULL, -- Gerando o UUID automaticamente
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Data e hora de criação
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- Atualização automática
    deleted_at TIMESTAMP NULL, -- Campo de data e hora de exclusão
    UNIQUE (uuid) -- Garantindo unicidade para o UUID
);
