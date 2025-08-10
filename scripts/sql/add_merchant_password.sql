-- 为商家表添加密码字段和状态字段
-- 执行前请备份数据库

-- 添加密码字段
ALTER TABLE merchants ADD COLUMN password VARCHAR(128) NOT NULL DEFAULT '' COMMENT '密码（加密存储）';

-- 添加状态字段
ALTER TABLE merchants ADD COLUMN status VARCHAR(16) NOT NULL DEFAULT 'active' COMMENT '状态：active/inactive';

-- 为手机号添加唯一约束（如果还没有的话）
ALTER TABLE merchants ADD UNIQUE INDEX idx_phone (phone);

-- 更新现有商家记录，设置默认密码为 '123456' 的base64编码
UPDATE merchants SET password = 'MTIzNDU2' WHERE password = '';

-- 显示更新后的表结构
DESCRIBE merchants;
