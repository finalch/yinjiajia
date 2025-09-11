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

 Date: 24/08/2025 00:21:19
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for categories
-- ----------------------------
DROP TABLE IF EXISTS `categories`;
CREATE TABLE `categories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `uuid` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '',
  `name` varchar(64) NOT NULL COMMENT '分类名称',
  `description` varchar(256) DEFAULT NULL COMMENT '分类描述',
  `icon_url` varchar(256) DEFAULT NULL COMMENT '分类图标URL',
  `sort_order` int DEFAULT '0' COMMENT '排序权重',
  `status` varchar(16) DEFAULT 'active' COMMENT '状态：active/inactive',
  `merchant_id` int NOT NULL COMMENT '所属商家ID',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_merchant_id` (`merchant_id`),
  KEY `idx_status` (`status`),
  KEY `idx_sort_order` (`sort_order`),
  CONSTRAINT `categories_ibfk_1` FOREIGN KEY (`merchant_id`) REFERENCES `merchants` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='商品分类表';

-- ----------------------------
-- Records of categories
-- ----------------------------
BEGIN;
INSERT INTO `categories` (`id`, `uuid`, `name`, `description`, `icon_url`, `sort_order`, `status`, `merchant_id`, `created_at`, `updated_at`) VALUES (1, 'a172a325-bf2f-8601-5bcc-20de443bb522', '手机数码', '智能手机、平板电脑、数码配件等', 'https://img.alicdn.com/imgextra/i1/O1CN01Z5paLz1UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg', 1, 'active', 1, '2025-08-17 00:16:41', '2025-08-17 00:18:40');
INSERT INTO `categories` (`id`, `uuid`, `name`, `description`, `icon_url`, `sort_order`, `status`, `merchant_id`, `created_at`, `updated_at`) VALUES (2, '14a9da92-75ee-edf2-0915-c329bcc1b713', '服装配饰', '男装、女装、童装、鞋靴、箱包等', 'https://img.alicdn.com/imgextra/i3/O1CN01c26iB51UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg', 2, 'active', 1, '2025-08-17 00:16:41', '2025-08-17 00:18:45');
INSERT INTO `categories` (`id`, `uuid`, `name`, `description`, `icon_url`, `sort_order`, `status`, `merchant_id`, `created_at`, `updated_at`) VALUES (3, 'b6ad668f-b3d7-9cd3-9733-96f46d27cd86', '家居生活', '家具、家纺、厨具、清洁用品等', 'https://img.alicdn.com/imgextra/i4/O1CN01FgolV51UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg', 3, 'active', 1, '2025-08-17 00:16:41', '2025-08-17 00:18:51');
INSERT INTO `categories` (`id`, `uuid`, `name`, `description`, `icon_url`, `sort_order`, `status`, `merchant_id`, `created_at`, `updated_at`) VALUES (4, 'bbf72fe7-4a0e-0fa2-ba6c-f543628b4a04', '美妆护肤', '护肤、彩妆、香水、个人护理等', 'https://img.alicdn.com/imgextra/i2/O1CN01Z5paLz1UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg', 4, 'active', 1, '2025-08-17 00:16:41', '2025-08-17 00:18:56');
INSERT INTO `categories` (`id`, `uuid`, `name`, `description`, `icon_url`, `sort_order`, `status`, `merchant_id`, `created_at`, `updated_at`) VALUES (5, '5ad92816-4bd9-96b0-4e4d-7f0601ca05db', '运动户外', '运动鞋服、健身器材、户外装备等', '', 5, 'inactive', 1, '2025-08-17 00:16:41', '2025-08-17 00:19:08');
INSERT INTO `categories` (`id`, `uuid`, `name`, `description`, `icon_url`, `sort_order`, `status`, `merchant_id`, `created_at`, `updated_at`) VALUES (6, '25b7046c-31cc-1df3-c844-c0e0d7c76c7a', '食品饮料', '零食、饮料、生鲜、保健品等', '', 6, 'active', 1, '2025-08-17 00:16:41', '2025-08-17 00:19:08');
INSERT INTO `categories` (`id`, `uuid`, `name`, `description`, `icon_url`, `sort_order`, `status`, `merchant_id`, `created_at`, `updated_at`) VALUES (7, '1cf69726-6b6b-4ef6-5252-7440bb2632a9', '图书音像', '图书、音像制品、教育用品等', '', 7, 'active', 1, '2025-08-17 00:16:41', '2025-08-17 00:19:13');
INSERT INTO `categories` (`id`, `uuid`, `name`, `description`, `icon_url`, `sort_order`, `status`, `merchant_id`, `created_at`, `updated_at`) VALUES (8, '042d1aa8-a502-e3b1-26e7-c3ca01852c62', '母婴用品', '奶粉、尿布、玩具、童装等', '', 8, 'active', 1, '2025-08-17 00:16:41', '2025-08-17 00:19:18');
COMMIT;

SET FOREIGN_KEY_CHECKS = 1;
