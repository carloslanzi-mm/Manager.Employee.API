CREATE TABLE company (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(60) NOT NULL,
    name VARCHAR(255) NOT NULL,
    contact_phone VARCHAR(20),
    contact_email VARCHAR(255),
    contact_person VARCHAR(255),
    service_type VARCHAR(100),
    partnership_started_at DATE,
    bank_name VARCHAR(100),
    agency VARCHAR(20),
    account_number VARCHAR(30),
    account_type ENUM('corrente', 'poupança') DEFAULT 'corrente',
    cnpj VARCHAR(14)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    UNIQUE (uuid)
);
