CREATE TABLE reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    report_type_id INT NOT NULL,
    url TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'completed', -- ou 'pending', 'failed'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at DATETIME NULL,
    FOREIGN KEY (report_type_id) REFERENCES report_type(id)
);
