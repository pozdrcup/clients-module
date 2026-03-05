-- Создание базы данных (выполнить отдельно под суперпользователем)
-- CREATE DATABASE clients_db;

-- Таблица клиентов
CREATE TABLE IF NOT EXISTS clients (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(200) NOT NULL,
    phone VARCHAR(30),
    email VARCHAR(100),
    registration_date DATE DEFAULT CURRENT_DATE,
    notes TEXT
);

-- Таблица заказов
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    amount NUMERIC(10, 2) NOT NULL DEFAULT 0,
    order_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(30) DEFAULT 'новый'
);
