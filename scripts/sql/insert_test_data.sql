-- 插入测试数据
-- 用户数据
INSERT INTO users (username, password, email, phone, created_at, updated_at) VALUES
('user001', 'password123', 'user001@example.com', '13800138001', NOW(), NOW()),
('user002', 'password123', 'user002@example.com', '13800138002', NOW(), NOW()),
('user003', 'password123', 'user003@example.com', '13800138003', NOW(), NOW()),
('user004', 'password123', 'user004@example.com', '13800138004', NOW(), NOW()),
('user005', 'password123', 'user005@example.com', '13800138005', NOW(), NOW());

-- 商家数据
INSERT INTO merchants (name, email, phone, created_at, updated_at) VALUES
('苹果官方旗舰店', 'apple@example.com', '400-123-4567', NOW(), NOW()),
('华为官方旗舰店', 'huawei@example.com', '400-123-4568', NOW(), NOW()),
('小米官方旗舰店', 'xiaomi@example.com', '400-123-4569', NOW(), NOW()),
('OPPO官方旗舰店', 'oppo@example.com', '400-123-4570', NOW(), NOW()),
('vivo官方旗舰店', 'vivo@example.com', '400-123-4571', NOW(), NOW());

-- 商品数据
INSERT INTO products (name, description, price, stock, image_url, video_url, category_id, merchant_id, status, created_at, updated_at) VALUES
('iPhone 15 Pro', '苹果最新旗舰手机，搭载A17 Pro芯片', 7999.00, 100, 'https://example.com/iphone15pro.jpg', 'https://example.com/iphone15pro.mp4', 1, 1, 'on_sale', NOW(), NOW()),
('iPhone 15', '苹果新一代iPhone，性能强劲', 5999.00, 150, 'https://example.com/iphone15.jpg', 'https://example.com/iphone15.mp4', 1, 1, 'on_sale', NOW(), NOW()),
('MacBook Pro 14', '专业级笔记本电脑，适合开发设计', 14999.00, 50, 'https://example.com/macbookpro.jpg', 'https://example.com/macbookpro.mp4', 1, 1, 'on_sale', NOW(), NOW()),
('华为 Mate 60 Pro', '华为旗舰手机，麒麟芯片', 6999.00, 80, 'https://example.com/mate60pro.jpg', 'https://example.com/mate60pro.mp4', 1, 2, 'on_sale', NOW(), NOW()),
('华为 P60 Pro', '华为影像旗舰', 5999.00, 120, 'https://example.com/p60pro.jpg', 'https://example.com/p60pro.mp4', 1, 2, 'on_sale', NOW(), NOW()),
('小米 14 Pro', '小米旗舰手机，徕卡影像', 4999.00, 200, 'https://example.com/mi14pro.jpg', 'https://example.com/mi14pro.mp4', 1, 3, 'on_sale', NOW(), NOW()),
('小米 14', '小米新一代旗舰', 3999.00, 180, 'https://example.com/mi14.jpg', 'https://example.com/mi14.mp4', 1, 3, 'on_sale', NOW(), NOW()),
('OPPO Find X7', 'OPPO影像旗舰', 5999.00, 90, 'https://example.com/findx7.jpg', 'https://example.com/findx7.mp4', 1, 4, 'on_sale', NOW(), NOW()),
('vivo X100 Pro', 'vivo影像旗舰', 5999.00, 110, 'https://example.com/x100pro.jpg', 'https://example.com/x100pro.mp4', 1, 5, 'on_sale', NOW(), NOW()),
('Nike Air Max', '经典运动鞋，舒适透气', 899.00, 300, 'https://example.com/nike.jpg', 'https://example.com/nike.mp4', 2, 1, 'on_sale', NOW(), NOW()),
('Adidas Ultraboost', '专业跑步鞋', 1299.00, 200, 'https://example.com/adidas.jpg', 'https://example.com/adidas.mp4', 2, 1, 'on_sale', NOW(), NOW()),
('机械键盘', '青轴机械键盘，游戏办公两用', 299.00, 500, 'https://example.com/keyboard.jpg', 'https://example.com/keyboard.mp4', 1, 3, 'on_sale', NOW(), NOW()),
('无线鼠标', '2.4G无线鼠标，静音设计', 99.00, 800, 'https://example.com/mouse.jpg', 'https://example.com/mouse.mp4', 1, 3, 'on_sale', NOW(), NOW()),
('蓝牙耳机', '主动降噪蓝牙耳机', 399.00, 400, 'https://example.com/headphone.jpg', 'https://example.com/headphone.mp4', 1, 4, 'on_sale', NOW(), NOW()),
('智能手表', '多功能智能手表', 1299.00, 150, 'https://example.com/watch.jpg', 'https://example.com/watch.mp4', 1, 5, 'on_sale', NOW(), NOW());

-- 订单数据
INSERT INTO orders (user_id, merchant_id, total_amount, status, created_at, updated_at) VALUES
(1, 1, 7999.00, 'paid', DATE_SUB(NOW(), INTERVAL 5 DAY), DATE_SUB(NOW(), INTERVAL 5 DAY)),
(2, 1, 5999.00, 'shipped', DATE_SUB(NOW(), INTERVAL 4 DAY), DATE_SUB(NOW(), INTERVAL 3 DAY)),
(3, 2, 6999.00, 'delivered', DATE_SUB(NOW(), INTERVAL 3 DAY), DATE_SUB(NOW(), INTERVAL 2 DAY)),
(4, 3, 4999.00, 'paid', DATE_SUB(NOW(), INTERVAL 2 DAY), DATE_SUB(NOW(), INTERVAL 2 DAY)),
(5, 4, 5999.00, 'pending', DATE_SUB(NOW(), INTERVAL 1 DAY), DATE_SUB(NOW(), INTERVAL 1 DAY)),
(1, 5, 5999.00, 'paid', NOW(), NOW()),
(2, 1, 14999.00, 'shipped', DATE_SUB(NOW(), INTERVAL 6 DAY), DATE_SUB(NOW(), INTERVAL 5 DAY)),
(3, 2, 5999.00, 'delivered', DATE_SUB(NOW(), INTERVAL 7 DAY), DATE_SUB(NOW(), INTERVAL 6 DAY)),
(4, 3, 3999.00, 'paid', DATE_SUB(NOW(), INTERVAL 8 DAY), DATE_SUB(NOW(), INTERVAL 8 DAY)),
(5, 4, 5999.00, 'cancelled', DATE_SUB(NOW(), INTERVAL 9 DAY), DATE_SUB(NOW(), INTERVAL 9 DAY));

-- 物流数据
INSERT INTO logistics (order_id, company, tracking_number, status, created_at, updated_at) VALUES
(2, '顺丰速运', 'SF1234567890', '运输中', DATE_SUB(NOW(), INTERVAL 3 DAY), NOW()),
(3, '中通快递', 'ZT1234567890', '已签收', DATE_SUB(NOW(), INTERVAL 2 DAY), DATE_SUB(NOW(), INTERVAL 1 DAY)),
(7, '圆通速递', 'YT1234567890', '运输中', DATE_SUB(NOW(), INTERVAL 5 DAY), NOW()),
(8, '京东物流', 'JD1234567890', '已签收', DATE_SUB(NOW(), INTERVAL 6 DAY), DATE_SUB(NOW(), INTERVAL 5 DAY));

-- 评价数据
INSERT INTO reviews (user_id, product_id, content, rating, image_url, video_url, created_at, updated_at) VALUES
(1, 1, 'iPhone 15 Pro真的很棒，性能强劲，拍照效果很好！', 5, 'https://example.com/review1.jpg', NULL, DATE_SUB(NOW(), INTERVAL 3 DAY), DATE_SUB(NOW(), INTERVAL 3 DAY)),
(2, 2, 'iPhone 15性价比很高，值得购买', 4, NULL, NULL, DATE_SUB(NOW(), INTERVAL 2 DAY), DATE_SUB(NOW(), INTERVAL 2 DAY)),
(3, 4, '华为Mate 60 Pro的拍照效果非常出色', 5, 'https://example.com/review3.jpg', 'https://example.com/review3.mp4', DATE_SUB(NOW(), INTERVAL 1 DAY), DATE_SUB(NOW(), INTERVAL 1 DAY)),
(4, 6, '小米14 Pro的徕卡影像系统很棒', 4, NULL, NULL, NOW(), NOW()),
(5, 8, 'OPPO Find X7的外观设计很漂亮', 4, 'https://example.com/review5.jpg', NULL, DATE_SUB(NOW(), INTERVAL 1 DAY), DATE_SUB(NOW(), INTERVAL 1 DAY)),
(1, 3, 'MacBook Pro性能很强，适合专业工作', 5, NULL, NULL, DATE_SUB(NOW(), INTERVAL 4 DAY), DATE_SUB(NOW(), INTERVAL 4 DAY)),
(2, 5, '华为P60 Pro的影像系统很专业', 4, 'https://example.com/review7.jpg', NULL, DATE_SUB(NOW(), INTERVAL 2 DAY), DATE_SUB(NOW(), INTERVAL 2 DAY)),
(3, 7, '小米14的性价比很高', 4, NULL, NULL, DATE_SUB(NOW(), INTERVAL 1 DAY), DATE_SUB(NOW(), INTERVAL 1 DAY)),
(4, 9, 'vivo X100 Pro的拍照效果很好', 5, 'https://example.com/review9.jpg', NULL, NOW(), NOW()),
(5, 10, 'Nike Air Max穿着很舒适', 4, NULL, NULL, DATE_SUB(NOW(), INTERVAL 3 DAY), DATE_SUB(NOW(), INTERVAL 3 DAY));

-- 账户数据
INSERT INTO accounts (merchant_id, balance, bank_account, created_at, updated_at) VALUES
(1, 5000.00, '6222021234567890123', NOW(), NOW()),
(2, 3000.00, '6222021234567890124', NOW(), NOW()),
(3, 4000.00, '6222021234567890125', NOW(), NOW()),
(4, 2000.00, '6222021234567890126', NOW(), NOW()),
(5, 3500.00, '6222021234567890127', NOW(), NOW()); 