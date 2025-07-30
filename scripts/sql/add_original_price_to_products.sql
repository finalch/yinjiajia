-- 为products表添加original_price字段
ALTER TABLE products ADD COLUMN IF NOT EXISTS original_price DECIMAL(10,2) NULL COMMENT '原价（用于促销显示）';

-- 更新现有商品的original_price（如果没有原价，设置为NULL）
UPDATE products SET original_price = NULL WHERE original_price = 0 OR original_price IS NULL; 