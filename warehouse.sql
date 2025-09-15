-- 仓库管理表
-- 用于存储商家的仓库信息

CREATE TABLE IF NOT EXISTS `warehouses` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '仓库ID',
  `merchant_id` int(11) NOT NULL COMMENT '商家ID',
  `name` varchar(100) NOT NULL COMMENT '仓库名称',
  `address` text NOT NULL COMMENT '仓库地址',
  `contact_person` varchar(50) NOT NULL COMMENT '联系人',
  `contact_phone` varchar(20) NOT NULL COMMENT '联系电话',
  `remark` text COMMENT '备注信息',
  `status` enum('active','inactive') NOT NULL DEFAULT 'active' COMMENT '状态：active-启用，inactive-禁用',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_merchant_id` (`merchant_id`),
  KEY `idx_status` (`status`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='仓库信息表';

-- 插入示例数据（可选）
INSERT INTO `warehouses` (`merchant_id`, `name`, `address`, `contact_person`, `contact_phone`, `remark`, `status`) VALUES
(1, '北京总仓', '北京市朝阳区xxx街道xxx号', '张三', '13800138001', '主要仓库', 'active'),
(1, '上海分仓', '上海市浦东新区xxx路xxx号', '李四', '13800138002', '华东地区仓库', 'active'),
(2, '广州分仓', '广州市天河区xxx大道xxx号', '王五', '13800138003', '华南地区仓库', 'active');

-- 如果需要为现有商家创建默认仓库，可以使用以下语句：
-- INSERT INTO `warehouses` (`merchant_id`, `name`, `address`, `contact_person`, `contact_phone`, `remark`, `status`)
-- SELECT id, CONCAT('默认仓库-', shop_name), address, contact_person, contact_phone, '系统默认创建的仓库', 'active'
-- FROM merchants WHERE id NOT IN (SELECT DISTINCT merchant_id FROM warehouses);
