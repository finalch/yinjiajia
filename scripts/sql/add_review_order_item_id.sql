-- 添加评价表的order_item_id字段并移除冗余的product_id字段
-- 用于关联具体的订单项

-- 添加order_item_id字段
ALTER TABLE reviews ADD COLUMN order_item_id INT;

-- 添加外键约束
ALTER TABLE reviews ADD CONSTRAINT fk_reviews_order_item 
    FOREIGN KEY (order_item_id) REFERENCES order_items(id);

-- 移除冗余的product_id字段（因为可以通过order_item_id获取）
ALTER TABLE reviews DROP COLUMN product_id;

-- 添加索引以提高查询性能
CREATE INDEX idx_reviews_order_item_id ON reviews(order_item_id);

-- 添加复合索引
CREATE INDEX idx_reviews_user_order_item ON reviews(user_id, order_item_id);

-- 为order_items表添加评价状态字段
ALTER TABLE order_items ADD COLUMN is_reviewed BOOLEAN DEFAULT FALSE;
ALTER TABLE order_items ADD COLUMN reviewed_at DATETIME;

-- 添加索引
CREATE INDEX idx_order_items_is_reviewed ON order_items(is_reviewed);
