-- 修复cart表的唯一约束
-- 首先查看现有的约束
SHOW CREATE TABLE cart;

-- 检查外键约束
SELECT 
    CONSTRAINT_NAME,
    COLUMN_NAME,
    REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME
FROM information_schema.KEY_COLUMN_USAGE 
WHERE TABLE_SCHEMA = 'ecommerce_db' 
AND TABLE_NAME = 'cart' 
AND REFERENCED_TABLE_NAME IS NOT NULL;

-- 检查唯一约束
SELECT 
    CONSTRAINT_NAME,
    COLUMN_NAME
FROM information_schema.KEY_COLUMN_USAGE 
WHERE TABLE_SCHEMA = 'ecommerce_db' 
AND TABLE_NAME = 'cart' 
AND CONSTRAINT_NAME = 'unique_user_product';

-- 如果存在错误约束，先删除外键约束，然后重新创建
-- 注意：这里需要根据实际的约束名称来调整

-- 方案1：如果unique_user_product是唯一约束而不是外键约束
-- ALTER TABLE cart DROP INDEX unique_user_product;

-- 方案2：如果是复合约束，可能需要先删除表重新创建
-- 或者修改约束定义

-- 添加正确的唯一约束（如果不存在的话）
-- ALTER TABLE cart ADD UNIQUE KEY unique_user_product_spec (user_id, product_id, spec_combination_id); 