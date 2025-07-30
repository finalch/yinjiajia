-- 创建订单商品表
CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    quantity INT NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 为orders表添加order_number字段（如果不存在）
ALTER TABLE orders ADD COLUMN IF NOT EXISTS order_number VARCHAR(50) UNIQUE NOT NULL DEFAULT '';

-- 更新现有订单的order_number
UPDATE orders SET order_number = CONCAT('ORD', DATE_FORMAT(created_at, '%Y%m%d%H%i%s'), LPAD(id, 6, '0')) WHERE order_number = ''; 