-- 为products表添加detail字段
ALTER TABLE products ADD COLUMN detail TEXT COMMENT '商品详情（富文本）';

-- 更新现有记录的detail字段为空字符串
UPDATE products SET detail = '' WHERE detail IS NULL; 