CREATE TABLE documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    type_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    url TEXT NOT NULL,
    started_at DATE,
    ended_at DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,

    FOREIGN KEY (company_id) REFERENCES company(id),
    FOREIGN KEY (type_id) REFERENCES type(id)
);
