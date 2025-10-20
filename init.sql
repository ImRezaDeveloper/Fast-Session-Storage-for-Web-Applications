CREATE TABLE inventory_category (
    id SERIAL PRIMARY KEY,
    parent_id INTEGER REFERENCES inventory_category(id) ON DELETE RESTRICT,
    name VARCHAR(50) UNIQUE NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    level SMALLINT NOT NULL DEFAULT 0
);

CREATE TABLE inventory_product (
    id SERIAL PRIMARY KEY,
    category_id INTEGER
        REFERENCES inventory_category(id) ON DELETE CASCADE,
    name VARCHAR(50) UNIQUE NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    is_digital BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    price NUMERIC(10, 2) NOT NULL
);
