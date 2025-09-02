CREATE DATABASE IF NOT EXISTS recipe_db;
USE recipe_db;

CREATE TABLE IF NOT EXISTS recipe_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ingredients TEXT,
    result_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
