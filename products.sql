/*
 Navicat Premium Dump SQL

 Source Server         : local
 Source Server Type    : MySQL
 Source Server Version : 80041 (8.0.41)
 Source Host           : localhost:3306
 Source Schema         : yinjiajia

 Target Server Type    : MySQL
 Target Server Version : 80041 (8.0.41)
 File Encoding         : 65001

 Date: 26/08/2025 23:43:49
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for product_spec_combinations
-- ----------------------------
DROP TABLE IF EXISTS `product_spec_combinations`;
CREATE TABLE `product_spec_combinations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `product_id` int NOT NULL COMMENT '商品ID',
  `spec_values` text NOT NULL COMMENT '规格值组合，JSON格式存储',
  `price` decimal(10,2) NOT NULL COMMENT '该规格组合的价格',
  `stock` int DEFAULT '0' COMMENT '该规格组合的库存',
  `image_url` varchar(256) DEFAULT NULL COMMENT '该规格组合的图片',
  `status` varchar(16) DEFAULT 'active' COMMENT '状态：active/inactive',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_product_id` (`product_id`),
  KEY `idx_status` (`status`),
  CONSTRAINT `fk_product_spec_combinations_product_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=52 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='商品规格组合表';

-- ----------------------------
-- Records of product_spec_combinations
-- ----------------------------
BEGIN;
INSERT INTO `product_spec_combinations` (`id`, `product_id`, `spec_values`, `price`, `stock`, `image_url`, `status`, `created_at`, `updated_at`) VALUES (39, 13, '{\"尺寸\":\"大\"}', 20.00, 0, '', 'active', '2025-08-16 20:19:57', '2025-08-17 12:21:12');
INSERT INTO `product_spec_combinations` (`id`, `product_id`, `spec_values`, `price`, `stock`, `image_url`, `status`, `created_at`, `updated_at`) VALUES (40, 13, '{\"尺寸\":\"中\"}', 10.00, 30, '', 'active', '2025-08-16 20:19:57', '2025-08-16 20:19:57');
INSERT INTO `product_spec_combinations` (`id`, `product_id`, `spec_values`, `price`, `stock`, `image_url`, `status`, `created_at`, `updated_at`) VALUES (41, 13, '{\"尺寸\":\"小\"}', 10.00, 10, '', 'active', '2025-08-16 20:19:57', '2025-08-16 20:19:57');
INSERT INTO `product_spec_combinations` (`id`, `product_id`, `spec_values`, `price`, `stock`, `image_url`, `status`, `created_at`, `updated_at`) VALUES (42, 14, '{\"颜色\":\"红色\",\"尺寸\":\"M\"}', 60.00, 2, '', 'active', '2025-08-17 08:04:33', '2025-08-21 14:58:22');
INSERT INTO `product_spec_combinations` (`id`, `product_id`, `spec_values`, `price`, `stock`, `image_url`, `status`, `created_at`, `updated_at`) VALUES (43, 14, '{\"颜色\":\"红色\",\"尺寸\":\"L\"}', 60.00, 2, '', 'active', '2025-08-17 08:04:33', '2025-08-17 08:04:33');
INSERT INTO `product_spec_combinations` (`id`, `product_id`, `spec_values`, `price`, `stock`, `image_url`, `status`, `created_at`, `updated_at`) VALUES (44, 14, '{\"颜色\":\"红色\",\"尺寸\":\"XL\"}', 60.00, 5, '', 'active', '2025-08-17 08:04:33', '2025-08-17 08:04:33');
INSERT INTO `product_spec_combinations` (`id`, `product_id`, `spec_values`, `price`, `stock`, `image_url`, `status`, `created_at`, `updated_at`) VALUES (45, 14, '{\"颜色\":\"蓝色\",\"尺寸\":\"M\"}', 60.00, 4, '', 'active', '2025-08-17 08:04:33', '2025-08-17 08:04:33');
INSERT INTO `product_spec_combinations` (`id`, `product_id`, `spec_values`, `price`, `stock`, `image_url`, `status`, `created_at`, `updated_at`) VALUES (46, 14, '{\"颜色\":\"蓝色\",\"尺寸\":\"L\"}', 60.00, 2, '', 'active', '2025-08-17 08:04:33', '2025-08-17 08:04:33');
INSERT INTO `product_spec_combinations` (`id`, `product_id`, `spec_values`, `price`, `stock`, `image_url`, `status`, `created_at`, `updated_at`) VALUES (47, 14, '{\"颜色\":\"蓝色\",\"尺寸\":\"XL\"}', 60.00, 2, '', 'active', '2025-08-17 08:04:33', '2025-08-17 08:04:33');
INSERT INTO `product_spec_combinations` (`id`, `product_id`, `spec_values`, `price`, `stock`, `image_url`, `status`, `created_at`, `updated_at`) VALUES (48, 15, '{\"颜色\":\"红色\",\"尺寸\":\"M\"}', 100.00, 6, '', 'active', '2025-08-17 12:05:36', '2025-08-21 14:58:22');
INSERT INTO `product_spec_combinations` (`id`, `product_id`, `spec_values`, `price`, `stock`, `image_url`, `status`, `created_at`, `updated_at`) VALUES (49, 15, '{\"颜色\":\"红色\",\"尺寸\":\"L\"}', 100.00, 20, '', 'active', '2025-08-17 12:05:36', '2025-08-17 12:05:36');
INSERT INTO `product_spec_combinations` (`id`, `product_id`, `spec_values`, `price`, `stock`, `image_url`, `status`, `created_at`, `updated_at`) VALUES (50, 15, '{\"颜色\":\"蓝色\",\"尺寸\":\"M\"}', 100.00, 30, '', 'active', '2025-08-17 12:05:36', '2025-08-17 12:05:36');
INSERT INTO `product_spec_combinations` (`id`, `product_id`, `spec_values`, `price`, `stock`, `image_url`, `status`, `created_at`, `updated_at`) VALUES (51, 15, '{\"颜色\":\"蓝色\",\"尺寸\":\"L\"}', 60.00, 20, '', 'active', '2025-08-17 12:05:36', '2025-08-17 12:05:36');
COMMIT;

-- ----------------------------
-- Table structure for product_specs
-- ----------------------------
DROP TABLE IF EXISTS `product_specs`;
CREATE TABLE `product_specs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `product_id` int NOT NULL COMMENT '商品ID',
  `name` varchar(64) NOT NULL COMMENT '规格名称（如：颜色、尺寸）',
  `values` text NOT NULL COMMENT '规格值列表，JSON格式存储',
  `sort_order` int DEFAULT '0' COMMENT '排序权重',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_product_id` (`product_id`),
  KEY `idx_sort_order` (`sort_order`),
  CONSTRAINT `fk_product_specs_product_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='商品规格表';

-- ----------------------------
-- Records of product_specs
-- ----------------------------
BEGIN;
INSERT INTO `product_specs` (`id`, `product_id`, `name`, `values`, `sort_order`, `created_at`, `updated_at`) VALUES (19, 13, '尺寸', '[\"大\",\"中\",\"小\"]', 0, '2025-08-16 20:19:57', '2025-08-16 20:19:57');
INSERT INTO `product_specs` (`id`, `product_id`, `name`, `values`, `sort_order`, `created_at`, `updated_at`) VALUES (20, 14, '颜色', '[\"红色\",\"蓝色\"]', 2, '2025-08-17 08:04:33', '2025-08-17 08:04:33');
INSERT INTO `product_specs` (`id`, `product_id`, `name`, `values`, `sort_order`, `created_at`, `updated_at`) VALUES (21, 14, '尺寸', '[\"M\",\"L\",\"XL\"]', 1, '2025-08-17 08:04:33', '2025-08-17 08:04:33');
INSERT INTO `product_specs` (`id`, `product_id`, `name`, `values`, `sort_order`, `created_at`, `updated_at`) VALUES (22, 15, '颜色', '[\"红色\",\"蓝色\"]', 0, '2025-08-17 12:05:36', '2025-08-17 12:05:36');
INSERT INTO `product_specs` (`id`, `product_id`, `name`, `values`, `sort_order`, `created_at`, `updated_at`) VALUES (23, 15, '尺寸', '[\"M\",\"L\"]', 1, '2025-08-17 12:05:36', '2025-08-17 12:05:36');
COMMIT;

-- ----------------------------
-- Table structure for products
-- ----------------------------
DROP TABLE IF EXISTS `products`;
CREATE TABLE `products` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL COMMENT '商品名称',
  `description` text COMMENT '商品描述',
  `price` float NOT NULL COMMENT '商品价格',
  `stock` int NOT NULL DEFAULT '0' COMMENT '库存数量',
  `image_url` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci COMMENT '商品图片URL',
  `video_url` varchar(256) DEFAULT NULL COMMENT '商品视频URL',
  `category_uuid` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '品类',
  `group_id` int DEFAULT NULL COMMENT '分组',
  `merchant_id` int NOT NULL COMMENT '所属商家ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `status` varchar(16) NOT NULL DEFAULT 'pending' COMMENT '商品状态：pending(审核中)/on_sale(已上架)/off_sale(已下架)/rejected(审核失败)',
  `has_specs` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否有规格',
  `original_price` decimal(10,2) DEFAULT NULL COMMENT '原价（用于促销显示）',
  `detail` text COMMENT '商品详情（富文本）',
  PRIMARY KEY (`id`),
  KEY `idx_merchant_id` (`merchant_id`),
  KEY `idx_price` (`price`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='商品表';

-- ----------------------------
-- Records of products
-- ----------------------------
BEGIN;
INSERT INTO `products` (`id`, `name`, `description`, `price`, `stock`, `image_url`, `video_url`, `category_uuid`, `group_id`, `merchant_id`, `created_at`, `updated_at`, `status`, `has_specs`, `original_price`, `detail`) VALUES (13, '一个小板凳', '一个小板凳一个小板凳一个小板凳一个小板凳', 10, 50, 'https://img12.360buyimg.com/n5/s720x720_jfs/t1/110781/9/39729/35768/6630b66eF7b8cbb65/a9cfa77aa778f872.jpg$%%$https://img12.360buyimg.com/n5/s720x720_jfs/t1/110781/9/39729/35768/6630b66eF7b8cbb65/a9cfa77aa778f872.jpg', '', 'b6ad668f-b3d7-9cd3-9733-96f46d27cd86', 4, 1, '2025-08-16 20:19:57', '2025-08-17 04:46:27', 'on_sale', 1, NULL, '<p>一个小板凳</p>');
INSERT INTO `products` (`id`, `name`, `description`, `price`, `stock`, `image_url`, `video_url`, `category_uuid`, `group_id`, `merchant_id`, `created_at`, `updated_at`, `status`, `has_specs`, `original_price`, `detail`) VALUES (14, ' 三彩2025夏季新款莱赛尔连衣裙圆领系带背心裙宽松长裙M', ' 三彩2025夏季新款莱赛尔连衣裙圆领系带背心裙宽松长裙M 三彩2025夏季新款莱赛尔连衣裙圆领系带背心裙宽松长裙M 三彩2025夏季新款莱赛尔连衣裙圆领系带背心裙宽松长裙M', 60, 21, 'https://img10.360buyimg.com/n5/s720x720_jfs/t1/326464/30/4493/73435/689d9155F5ac8407a/94dc11a7f96a0732.jpg', '', '2', 4, 1, '2025-08-17 08:04:33', '2025-08-17 16:05:05', 'on_sale', 1, NULL, '<p><span style=\"color: rgb(26, 26, 26); background-color: rgb(255, 255, 255);\"> 三彩2025夏季新款莱赛尔连衣裙圆领系带背心裙宽松长裙M 三彩2025夏季新款莱赛尔连衣裙圆领系带背心裙宽松长裙M 三彩2025夏季新款莱赛尔连衣裙圆领系带背心裙宽松长裙M 三彩2025夏季新款莱赛尔连衣裙圆领系带背心裙宽松长裙M 三彩2025夏季新款莱赛尔连衣裙圆领系带背心裙宽松长裙M 三彩2025夏季新款莱赛尔连衣裙圆领系带背心裙宽松长裙M 三彩2025夏季新款莱赛尔连衣裙圆领系带背心裙宽松长裙M 三彩2025夏季新款莱赛尔连衣裙圆领系带背心裙宽松长裙M 三彩2025夏季新款莱赛尔连衣裙圆领系带背心裙宽松长裙M 三彩2025夏季新款莱赛尔连衣裙圆领系带背心裙宽松长裙M 三彩2025夏季新款莱赛尔连衣裙圆领系带背心裙宽松长裙M 三彩2025夏季新款莱赛尔连衣裙圆领系带背心裙宽松长裙M 三彩2025夏季新款莱赛尔连衣裙圆领系带背心裙宽松长裙M 三彩2025夏季新款莱赛尔连衣裙圆领系带背心裙宽松长裙M 三彩2025夏季新款莱赛尔连衣裙圆领系带背心裙宽松长裙M 三彩2025夏季新款莱赛尔连衣裙圆领系带背心裙宽松长裙M 三彩2025夏季新款莱赛尔连衣裙圆领系带背心裙宽松长裙M</span></p>');
INSERT INTO `products` (`id`, `name`, `description`, `price`, `stock`, `image_url`, `video_url`, `category_uuid`, `group_id`, `merchant_id`, `created_at`, `updated_at`, `status`, `has_specs`, `original_price`, `detail`) VALUES (15, '新-三彩2025夏季新款莱赛尔连衣裙圆领系带背心裙宽松长裙M', '三彩2025夏季新款莱赛尔连衣裙圆领系带背心裙宽松长裙M三彩2025夏季新款莱赛尔连衣裙圆领系带背心裙宽松长裙M三彩2025夏季新款莱赛尔连衣裙圆领系带背心裙宽松长裙M', 60, 80, 'https://img12.360buyimg.com/n5/s720x720_jfs/t1/110781/9/39729/35768/6630b66eF7b8cbb65/a9cfa77aa778f872.jpg$%%$https://img12.360buyimg.com/n5/s720x720_jfs/t1/110781/9/39729/35768/6630b66eF7b8cbb65/a9cfa77aa778f872.jpg', '', '2', 2, 1, '2025-08-17 12:05:36', '2025-08-17 12:13:34', 'on_sale', 1, NULL, '<h1 style=\"text-align: start;\"></h1><h1 style=\"text-align: start;\">三彩2025夏季新款莱赛尔连衣裙圆领系带背心裙宽松长裙M</h1><h1 style=\"text-align: start;\">三彩2025夏季新款莱赛尔连衣裙圆领系带背心裙宽松长裙M</h1><h1 style=\"text-align: start;\">三彩2025夏季新款莱赛尔连衣裙圆领系带背心裙宽松长裙M</h1>');
COMMIT;

SET FOREIGN_KEY_CHECKS = 1;
