CREATE TABLE address (
    id INT AUTO_INCREMENT PRIMARY KEY,
    street VARCHAR(255) NOT NULL,
    number VARCHAR(50),
    neighbor VARCHAR(255),
    zip_code VARCHAR(20),
    company_id INT NOT NULL UNIQUE, -- Garantindo 1:1 com company
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    FOREIGN KEY (company_id) REFERENCES company(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
