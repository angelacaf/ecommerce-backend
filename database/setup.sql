-- Crea il database ed entra
CREATE DATABASE ecommerce_db
    WITH OWNER = postgres
    ENCODING = 'UTF8';

\c ecommerce_db

-- Crea uno schema dedicato
CREATE SCHEMA ecommerce;

SET search_path TO ecommerce;

-- Tabelle di dominio
CREATE TABLE ecommerce.categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX idx_categories_name ON ecommerce.categories(name);
CREATE INDEX idx_categories_active ON ecommerce.categories(active);

-- Tabelle principali
CREATE TABLE ecommerce.users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    postal_code VARCHAR(10),
    state VARCHAR(50),
    country VARCHAR(100) DEFAULT 'Italy',
    active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_active ON ecommerce.users(active);
CREATE INDEX idx_users_email ON ecommerce.users(email);

CREATE TABLE ecommerce.products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price NUMERIC(10,2) NOT NULL CHECK (price >= 0),
    available_quantity INTEGER NOT NULL DEFAULT 0 CHECK (available_quantity >= 0),
    image_url VARCHAR(500),
    sku VARCHAR(100) UNIQUE,
    active BOOLEAN DEFAULT TRUE,
    featured BOOLEAN DEFAULT FALSE,
    category_id INTEGER REFERENCES ecommerce.categories(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_active ON ecommerce.products(active);
CREATE INDEX idx_products_name ON ecommerce.products(name);
CREATE INDEX idx_products_price ON ecommerce.products(price);
CREATE INDEX idx_products_category_id ON ecommerce.products(category_id);

CREATE TABLE ecommerce.orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES ecommerce.users(id) ON DELETE CASCADE,
    order_number VARCHAR(50) NOT NULL UNIQUE,
    status VARCHAR(50) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending','paid','processing','shipped','delivered','cancelled','refunded')),
    total NUMERIC(10,2) NOT NULL CHECK (total >= 0),
    subtotal NUMERIC(10,2) NOT NULL CHECK (subtotal >= 0),
    shipping_cost NUMERIC(10,2) DEFAULT 0.00 CHECK (shipping_cost >= 0),
    tax NUMERIC(10,2) DEFAULT 0.00 CHECK (tax >= 0),
    discount NUMERIC(10,2) DEFAULT 0.00 CHECK (discount >= 0),
    discount_code VARCHAR(50),
    shipping_address TEXT NOT NULL,
    shipping_city VARCHAR(100),
    shipping_postal_code VARCHAR(10),
    shipping_state VARCHAR(50),
    shipping_country VARCHAR(100) DEFAULT 'Italy',
    notes TEXT,
    payment_intent_id VARCHAR(255),
    paid BOOLEAN DEFAULT FALSE,
    paid_at TIMESTAMP WITHOUT TIME ZONE,
    shipped_at TIMESTAMP WITHOUT TIME ZONE,
    delivered_at TIMESTAMP WITHOUT TIME ZONE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_orders_user ON ecommerce.orders(user_id);
CREATE INDEX idx_orders_created ON ecommerce.orders(created_at);
CREATE INDEX idx_orders_number ON ecommerce.orders(order_number);
CREATE INDEX idx_orders_status ON ecommerce.orders(status);

CREATE TABLE ecommerce.order_details (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES ecommerce.orders(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES ecommerce.products(id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10,2) NOT NULL CHECK (unit_price >= 0),
    subtotal NUMERIC(10,2) NOT NULL CHECK (subtotal >= 0)
);

CREATE INDEX idx_order_details_order ON ecommerce.order_details(order_id);
CREATE INDEX idx_order_details_product ON ecommerce.order_details(product_id);

-- Dati di esempio
INSERT INTO ecommerce.categories (name, description, active) VALUES
('Food', 'Prodotti alimentari e bevande', TRUE),
('Elettronica', 'Dispositivi elettronici, computer, smartphone e accessori', TRUE),
('Moda', 'Abbigliamento, scarpe e accessori moda', TRUE),
('Sport', 'Articoli sportivi e attrezzature per il fitness', TRUE),
('Motori', 'Auto, moto e accessori per veicoli', TRUE),
('Collezionismo', 'Oggetti da collezione, antiquariato e memorabilia', TRUE),
('Black Friday', 'Super sconti e offerte speciali Black Friday', TRUE),
('Natale', 'Decorazioni natalizie, regali e articoli per le feste', TRUE);

INSERT INTO ecommerce.users (email, password_hash, first_name, last_name, phone, address, city, postal_code, country, active, email_verified, created_at, updated_at) VALUES
('mario.rossi@email.com', '$2b$12$hash1', 'Mario', 'Rossi', '+39 333 1234567', 'Via Roma 1', 'Rome', '00100', 'Italy', true, false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('luigi.verdi@email.com', '$2b$12$hash2', 'Luigi', 'Verdi', '+39 333 9876543', 'Via Milano 5', 'Milan', '20100', 'Italy', true, false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('anna.bianchi@email.com', '$2b$12$hash3', 'Anna', 'Bianchi', '+39 333 5556677', 'Via Napoli 10', 'Naples', '80100', 'Italy', true, false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

INSERT INTO ecommerce.products (name, description, price, available_quantity, sku, active, featured, created_at, updated_at, category_id) VALUES
('Red T-Shirt', '100% cotton t-shirt', 29.99, 100, 'TEE-RED-001', true, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 3),
('Blue Jeans', 'Slim fit jeans', 59.99, 50, 'JEA-BLU-001', true, false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 3),
('Nike Shoes', 'Running shoes', 89.99, 30, 'SHO-NIKE-001', true, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 3),
('Gray Hoodie', 'Hoodie with hood', 39.99, 75, 'HOO-GRAY-001', true, false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 3),
('Black Jacket', 'Waterproof jacket', 79.99, 20, 'JAC-BLK-001', true, false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 3);

INSERT INTO ecommerce.orders (user_id, order_number, status, total, subtotal, shipping_cost, tax, discount, shipping_address, shipping_city, shipping_postal_code, shipping_country, paid, paid_at, created_at, updated_at) VALUES
(1, 'ORD-2024-001', 'delivered', 124.98, 119.98, 5.00, 0.00, 0.00, 'Via Roma 1', 'Rome', '00100', 'Italy', true, '2024-11-10 14:30:00', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(1, 'ORD-2024-002', 'shipped', 89.99, 89.99, 0.00, 0.00, 0.00, 'Via Roma 1', 'Rome', '00100', 'Italy', true, '2024-11-15 10:20:00', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(2, 'ORD-2024-003', 'paid', 69.98, 59.98, 10.00, 0.00, 0.00, 'Via Milano 5', 'Milan', '20100', 'Italy', true, '2024-11-17 09:15:00', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(3, 'ORD-2024-004', 'pending', 44.99, 39.99, 5.00, 0.00, 0.00, 'Via Napoli 10', 'Naples', '80100', 'Italy', false, NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

INSERT INTO ecommerce.order_details (order_id, product_id, quantity, unit_price, subtotal) VALUES
(1, 1, 2, 29.99, 59.98),
(1, 2, 1, 59.99, 59.99),
(2, 3, 1, 89.99, 89.99),
(3, 1, 1, 29.99, 29.99),
(3, 4, 1, 39.99, 39.99),
(4, 4, 1, 39.99, 39.99);


ALTER TABLE ecommerce.users RENAME TO users;
