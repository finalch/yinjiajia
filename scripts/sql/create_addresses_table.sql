-- 创建收货地址表
CREATE TABLE IF NOT EXISTS `addresses` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL COMMENT '用户ID',
  `receiver_name` varchar(64) NOT NULL COMMENT '收货人姓名',
  `phone` varchar(20) NOT NULL COMMENT '收货人电话',
  `province` varchar(32) NOT NULL COMMENT '省份',
  `city` varchar(32) NOT NULL COMMENT '城市',
  `district` varchar(32) NOT NULL COMMENT '区县',
  `detail_address` varchar(256) NOT NULL COMMENT '详细地址',
  `is_default` tinyint(1) DEFAULT 0 COMMENT '是否默认地址',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_is_default` (`is_default`),
  CONSTRAINT `fk_addresses_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='收货地址表';

-- 插入测试数据
INSERT INTO `addresses` (`user_id`, `receiver_name`, `phone`, `province`, `city`, `district`, `detail_address`, `is_default`) VALUES
(1, '张三', '13800138001', '北京市', '北京市', '朝阳区', '三里屯SOHO 1号楼 1001室', 1),
(1, '李四', '13800138002', '上海市', '上海市', '浦东新区', '陆家嘴金融中心 2号楼 2002室', 0),
(2, '王五', '13800138003', '广州市', '广州市', '天河区', '珠江新城 3号楼 3003室', 1); 