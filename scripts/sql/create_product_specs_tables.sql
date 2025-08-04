-- 创建商品规格表
CREATE TABLE IF NOT EXISTS `product_specs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `product_id` int(11) NOT NULL COMMENT '商品ID',
  `name` varchar(64) NOT NULL COMMENT '规格名称（如：颜色、尺寸）',
  `values` text NOT NULL COMMENT '规格值列表，JSON格式存储',
  `sort_order` int(11) DEFAULT 0 COMMENT '排序权重',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_product_id` (`product_id`),
  KEY `idx_sort_order` (`sort_order`),
  CONSTRAINT `fk_product_specs_product_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品规格表';

-- 创建商品规格组合表
CREATE TABLE IF NOT EXISTS `product_spec_combinations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `product_id` int(11) NOT NULL COMMENT '商品ID',
  `spec_values` text NOT NULL COMMENT '规格值组合，JSON格式存储',
  `price` decimal(10,2) NOT NULL COMMENT '该规格组合的价格',
  `stock` int(11) DEFAULT 0 COMMENT '该规格组合的库存',
  `image_url` varchar(256) DEFAULT NULL COMMENT '该规格组合的图片',
  `status` varchar(16) DEFAULT 'active' COMMENT '状态：active/inactive',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_product_id` (`product_id`),
  KEY `idx_status` (`status`),
  CONSTRAINT `fk_product_spec_combinations_product_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品规格组合表';

-- 为products表添加has_specs字段
ALTER TABLE `products` ADD COLUMN `has_specs` tinyint(1) DEFAULT 0 COMMENT '是否有规格' AFTER `status`;

-- 为cart表添加spec_combination_id字段
ALTER TABLE `cart` ADD COLUMN `spec_combination_id` int(11) DEFAULT NULL COMMENT '规格组合ID' AFTER `product_id`;
ALTER TABLE `cart` ADD KEY `idx_spec_combination_id` (`spec_combination_id`);
ALTER TABLE `cart` ADD CONSTRAINT `fk_cart_spec_combination_id` FOREIGN KEY (`spec_combination_id`) REFERENCES `product_spec_combinations` (`id`) ON DELETE CASCADE;

-- 为order_items表添加spec_combination_id字段
ALTER TABLE `order_items` ADD COLUMN `spec_combination_id` int(11) DEFAULT NULL COMMENT '规格组合ID' AFTER `product_id`;
ALTER TABLE `order_items` ADD KEY `idx_spec_combination_id` (`spec_combination_id`);
ALTER TABLE `order_items` ADD CONSTRAINT `fk_order_items_spec_combination_id` FOREIGN KEY (`spec_combination_id`) REFERENCES `product_spec_combinations` (`id`) ON DELETE SET NULL;

-- 插入测试数据：商品规格示例
INSERT INTO `product_specs` (`product_id`, `name`, `values`, `sort_order`) VALUES
(1, '颜色', '["红色", "蓝色", "黑色"]', 1),
(1, '尺寸', '["S", "M", "L", "XL"]', 2),
(2, '颜色', '["白色", "黑色"]', 1),
(2, '尺寸', '["36", "37", "38", "39", "40"]', 2);

-- 插入测试数据：规格组合示例
INSERT INTO `product_spec_combinations` (`product_id`, `spec_values`, `price`, `stock`, `image_url`, `status`) VALUES
-- 商品1的规格组合
(1, '{"颜色": "红色", "尺寸": "S"}', 99.00, 10, '/static/product1-red-s.jpg', 'active'),
(1, '{"颜色": "红色", "尺寸": "M"}', 99.00, 15, '/static/product1-red-m.jpg', 'active'),
(1, '{"颜色": "红色", "尺寸": "L"}', 99.00, 8, '/static/product1-red-l.jpg', 'active'),
(1, '{"颜色": "红色", "尺寸": "XL"}', 99.00, 5, '/static/product1-red-xl.jpg', 'active'),
(1, '{"颜色": "蓝色", "尺寸": "S"}', 99.00, 12, '/static/product1-blue-s.jpg', 'active'),
(1, '{"颜色": "蓝色", "尺寸": "M"}', 99.00, 18, '/static/product1-blue-m.jpg', 'active'),
(1, '{"颜色": "蓝色", "尺寸": "L"}', 99.00, 10, '/static/product1-blue-l.jpg', 'active'),
(1, '{"颜色": "蓝色", "尺寸": "XL"}', 99.00, 7, '/static/product1-blue-xl.jpg', 'active'),
(1, '{"颜色": "黑色", "尺寸": "S"}', 109.00, 8, '/static/product1-black-s.jpg', 'active'),
(1, '{"颜色": "黑色", "尺寸": "M"}', 109.00, 12, '/static/product1-black-m.jpg', 'active'),
(1, '{"颜色": "黑色", "尺寸": "L"}', 109.00, 6, '/static/product1-black-l.jpg', 'active'),
(1, '{"颜色": "黑色", "尺寸": "XL"}', 109.00, 4, '/static/product1-black-xl.jpg', 'active'),

-- 商品2的规格组合（部分组合）
(2, '{"颜色": "白色", "尺寸": "36"}', 299.00, 5, '/static/product2-white-36.jpg', 'active'),
(2, '{"颜色": "白色", "尺寸": "37"}', 299.00, 8, '/static/product2-white-37.jpg', 'active'),
(2, '{"颜色": "白色", "尺寸": "38"}', 299.00, 12, '/static/product2-white-38.jpg', 'active'),
(2, '{"颜色": "白色", "尺寸": "39"}', 299.00, 6, '/static/product2-white-39.jpg', 'active'),
(2, '{"颜色": "白色", "尺寸": "40"}', 299.00, 3, '/static/product2-white-40.jpg', 'active'),
(2, '{"颜色": "黑色", "尺寸": "37"}', 329.00, 10, '/static/product2-black-37.jpg', 'active'),
(2, '{"颜色": "黑色", "尺寸": "38"}', 329.00, 15, '/static/product2-black-38.jpg', 'active'),
(2, '{"颜色": "黑色", "尺寸": "39"}', 329.00, 8, '/static/product2-black-39.jpg', 'active'),
(2, '{"颜色": "黑色", "尺寸": "40"}', 329.00, 5, '/static/product2-black-40.jpg', 'active');

-- 更新商品表，标记有规格的商品
UPDATE `products` SET `has_specs` = 1 WHERE `id` IN (1, 2); 