CREATE TABLE alerts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  document_id INT NOT NULL,
  alert_date DATE NOT NULL,
  sent_emails TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (document_id, alert_date)
);
