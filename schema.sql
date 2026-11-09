-- Create Product Dimensions Table
DROP TABLE IF EXISTS dim_products CASCADE;
CREATE TABLE dim_products (
    product_name VARCHAR(100) PRIMARY KEY,
    unit_price NUMERIC(10, 2) NOT NULL
);

-- Create Transactional Fact Table
DROP TABLE IF EXISTS fact_orders CASCADE;
CREATE TABLE fact_orders (
    order_id INT PRIMARY KEY,
    user_id INT NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    quantity INT NOT NULL,
    discount NUMERIC(4, 2) NOT NULL,
    net_revenue NUMERIC(10, 2) NOT NULL,
    order_timestamp TIMESTAMP NOT NULL,
    FOREIGN KEY (product_name) REFERENCES dim_products(product_name)
);