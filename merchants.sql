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

 Date: 24/08/2025 00:22:21
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for merchants
-- ----------------------------
DROP TABLE IF EXISTS `merchants`;
CREATE TABLE `merchants` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL COMMENT '商家名称',
  `email` varchar(120) DEFAULT NULL COMMENT '商家邮箱',
  `phone` varchar(20) DEFAULT NULL COMMENT '商家电话',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `password` varchar(128) NOT NULL DEFAULT '' COMMENT '密码（加密存储）',
  `status` varchar(16) NOT NULL DEFAULT 'active' COMMENT '状态：active/inactive',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `idx_phone` (`phone`),
  KEY `idx_name` (`name`),
  KEY `idx_email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='商家表';

-- ----------------------------
-- Records of merchants
-- ----------------------------
BEGIN;
INSERT INTO `merchants` (`id`, `name`, `email`, `phone`, `created_at`, `updated_at`, `password`, `status`) VALUES (1, '手机专卖店', 'merchant@example.com', '13800138000', '2025-07-20 13:29:06', '2025-08-10 21:54:07', 'MTIzNDU2', 'active');
INSERT INTO `merchants` (`id`, `name`, `email`, `phone`, `created_at`, `updated_at`, `password`, `status`) VALUES (2, '苹果旗舰店', NULL, NULL, '2025-08-10 00:55:37', '2025-08-10 21:54:07', 'MTIzNDU2', 'active');
INSERT INTO `merchants` (`id`, `name`, `email`, `phone`, `created_at`, `updated_at`, `password`, `status`) VALUES (3, 'M17548074919402445', NULL, '13100000000', '2025-08-10 14:31:32', '2025-08-10 14:31:32', 'MTIzNDU2', 'active');
COMMIT;

SET FOREIGN_KEY_CHECKS = 1;
