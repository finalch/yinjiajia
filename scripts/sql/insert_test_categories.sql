-- 插入测试商家数据（如果不存在）
INSERT IGNORE INTO merchants (id, name, email, phone, created_at, updated_at) VALUES
(1, '测试商家', 'test@example.com', '13800138000', NOW(), NOW());

-- 插入测试分类数据
INSERT INTO categories (name, description, icon_url, sort_order, status, merchant_id, created_at, updated_at) VALUES
('手机数码', '智能手机、平板电脑、数码配件等', 'https://img.alicdn.com/imgextra/i1/O1CN01Z5paLz1UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg', 1, 'active', 1, NOW(), NOW()),
('服装配饰', '男装、女装、童装、鞋靴、箱包等', 'https://img.alicdn.com/imgextra/i3/O1CN01c26iB51UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg', 2, 'active', 1, NOW(), NOW()),
('家居生活', '家具、家纺、厨具、清洁用品等', 'https://img.alicdn.com/imgextra/i4/O1CN01FgolV51UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg', 3, 'active', 1, NOW(), NOW()),
('美妆护肤', '护肤、彩妆、香水、个人护理等', 'https://img.alicdn.com/imgextra/i2/O1CN01Z5paLz1UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg', 4, 'active', 1, NOW(), NOW()),
('运动户外', '运动鞋服、健身器材、户外装备等', '', 5, 'inactive', 1, NOW(), NOW()),
('食品饮料', '零食、饮料、生鲜、保健品等', '', 6, 'active', 1, NOW(), NOW()),
('图书音像', '图书、音像制品、教育用品等', '', 7, 'active', 1, NOW(), NOW()),
('母婴用品', '奶粉、尿布、玩具、童装等', '', 8, 'active', 1, NOW(), NOW()); 