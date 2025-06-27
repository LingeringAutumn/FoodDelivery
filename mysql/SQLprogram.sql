SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 配送员信息表，记录配送员编号、姓名和联系方式
DROP TABLE IF EXISTS `dispatcher`;
CREATE TABLE `dispatcher`  (
  `dispatcher_id` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `dispatcher_name` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `dispatcher_phone` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  PRIMARY KEY (`dispatcher_id`) USING BTREE,
  UNIQUE INDEX `dispatcher_id`(`dispatcher_id`) USING BTREE,
  INDEX `dispatcher_name`(`dispatcher_name`) USING BTREE,
  INDEX `dispatcher_phone`(`dispatcher_phone`) USING BTREE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb3 ROW_FORMAT = DYNAMIC;

-- 初始化配送员数据
INSERT INTO `dispatcher` VALUES ('D001', '王小强', '13888880001');
INSERT INTO `dispatcher` VALUES ('D002', '李雪琴', '13888880002');
INSERT INTO `dispatcher` VALUES ('D003', '周杰伦', '13888880003');
INSERT INTO `dispatcher` VALUES ('D004', '韩梅梅', '13888880004');

-- 商家店铺表，记录菜品价格与销售量
DROP TABLE IF EXISTS `fastfood_shop`;
CREATE TABLE `fastfood_shop`  (
  `shop_name` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `price` int NOT NULL,
  `m_sale_v` int NOT NULL,
  PRIMARY KEY (`shop_name`) USING BTREE,
  UNIQUE INDEX `shop_name`(`shop_name`) USING BTREE,
  INDEX `price`(`price`) USING BTREE,
  INDEX `m_sale_v`(`m_sale_v`) USING BTREE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb3 ROW_FORMAT = DYNAMIC;

-- 初始化店铺信息
INSERT INTO `fastfood_shop` VALUES ('美味便当', 18, 77);
INSERT INTO `fastfood_shop` VALUES ('食尚快餐', 12, 134);
INSERT INTO `fastfood_shop` VALUES ('美食小站', 20, 89);
INSERT INTO `fastfood_shop` VALUES ('牛肉烧饭', 14, 102);
INSERT INTO `fastfood_shop` VALUES ('香辣鸡丁饭', 17, 83);
INSERT INTO `fastfood_shop` VALUES ('酸菜鱼盖饭', 16, 108);
INSERT INTO `fastfood_shop` VALUES ('排骨汤饭', 13, 97);
INSERT INTO `fastfood_shop` VALUES ('红烧鸡腿饭', 19, 62);

-- 用户订单信息表
DROP TABLE IF EXISTS `oorder`;
CREATE TABLE `oorder`  (
  `order_id` int NOT NULL AUTO_INCREMENT,
  `shop_name` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `order_money` int NOT NULL,
  `order_way` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `cons_phone` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `cons_name` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `cons_addre` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `checked` int NULL DEFAULT 0 COMMENT '订单状态：0-未派单，1-已揽单，2-商家备货中，3-已发货，4-派送中，5-已送达',
  `create_time` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`order_id`) USING BTREE,
  UNIQUE INDEX `order_id`(`order_id`) USING BTREE,
  INDEX `shop_name`(`shop_name`) USING BTREE,
  INDEX `order_money`(`order_money`) USING BTREE,
  INDEX `order_way`(`order_way`) USING BTREE,
  INDEX `cons_phone`(`cons_phone`) USING BTREE,
  INDEX `cons_name`(`cons_name`) USING BTREE,
  INDEX `cons_addre`(`cons_addre`) USING BTREE,
  INDEX `checked`(`checked`) USING BTREE,
  INDEX `create_time`(`create_time`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4 DEFAULT CHARSET = utf8mb3 ROW_FORMAT = DYNAMIC;

-- 初始化订单数据
INSERT INTO `oorder` VALUES (1, '美味便当', 18, '网上订餐', '13900000001', '张铁林', '6栋602', 0, '2023-10-11 11:15:00');
INSERT INTO `oorder` VALUES (2, '酸菜鱼盖饭', 16, '网上订餐', '13900000002', '刘德华', '5栋104', 2, '2023-10-11 11:20:00');
INSERT INTO `oorder` VALUES (3, '红烧鸡腿饭', 19, '人工订餐', '13900000003', '赵敏', '7栋305', 0, '2023-10-11 11:25:00');

-- 订单状态字典
DROP TABLE IF EXISTS `order_status_dict`;
CREATE TABLE order_status_dict (
  status_code INT PRIMARY KEY,
  status_desc VARCHAR(50) NOT NULL
);

INSERT INTO order_status_dict VALUES
(0, '未派单'),
(1, '已揽单'),
(2, '商家备货中'),
(3, '已发货'),
(4, '派送中'),
(5, '已送达');


-- 订餐方式统计表
DROP TABLE IF EXISTS `orderway`;
CREATE TABLE `orderway`  (
  `orderway_name` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `count` int NOT NULL,
  PRIMARY KEY (`orderway_name`) USING BTREE,
  UNIQUE INDEX `orderway_name`(`orderway_name`) USING BTREE,
  INDEX `count`(`count`) USING BTREE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb3 ROW_FORMAT = DYNAMIC;

-- 初始化订餐方式数据
INSERT INTO `orderway` VALUES ('网上订餐', 35);
INSERT INTO `orderway` VALUES ('人工订餐', 45);

-- 店员信息表，对应所在店铺
DROP TABLE IF EXISTS `server`;
CREATE TABLE `server`  (
  `service_id` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `service_name` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `fastfood_shop_name` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  PRIMARY KEY (`service_id`) USING BTREE,
  UNIQUE INDEX `service_id`(`service_id`) USING BTREE,
  INDEX `service_name`(`service_name`) USING BTREE,
  INDEX `fastfood_shop_name`(`fastfood_shop_name`) USING BTREE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb3 ROW_FORMAT = DYNAMIC;

-- 初始化服务员数据
INSERT INTO `server` VALUES ('S100', '阿康', '香辣鸡丁饭');
INSERT INTO `server` VALUES ('S101', '小美', '红烧鸡腿饭');
INSERT INTO `server` VALUES ('S102', '老杜', '食尚快餐');

-- 用户账号信息表，记录登录相关数据
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user`  (
  `id` int UNSIGNED NOT NULL AUTO_INCREMENT,
  `username` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `password` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `telephone` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `role` int NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `id`(`id`) USING BTREE,
  INDEX `username`(`username`) USING BTREE,
  INDEX `password`(`password`) USING BTREE,
  INDEX `telephone`(`telephone`) USING BTREE,
  INDEX `role`(`role`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4 DEFAULT CHARSET = utf8mb3 ROW_FORMAT = DYNAMIC;

-- 初始化用户数据
INSERT INTO `user` VALUES (2, 'alice', 'passw0rd', '13988888888', 0);
INSERT INTO `user` VALUES (3, 'bob', 'abc123456', '13777778888', 0);

-- 用户详细信息表，绑定账号ID
DROP TABLE IF EXISTS `user_msg`;
CREATE TABLE `user_msg`  (
  `id` int UNSIGNED NULL DEFAULT NULL,
  `real_name` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `sex` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `age` int NOT NULL,
  `mail` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `phone` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `user_name` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  INDEX `userid`(`id`) USING BTREE,
  INDEX `real_name`(`real_name`) USING BTREE,
  INDEX `sex`(`sex`) USING BTREE,
  INDEX `age`(`age`) USING BTREE,
  INDEX `mail`(`mail`) USING BTREE,
  INDEX `phone`(`phone`) USING BTREE,
  INDEX `user_name`(`user_name`) USING BTREE,
  CONSTRAINT `userid` FOREIGN KEY (`id`) REFERENCES `user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb3 ROW_FORMAT = DYNAMIC;

-- 初始化用户信息数据
INSERT INTO `user_msg` VALUES (2, '王一博', '男', 21, 'wyb@example.com', '13988888888', 'alice');
INSERT INTO `user_msg` VALUES (3, '赵小花', '女', 19, 'zxh@example.com', '13777778888', 'bob');

-- 物流配送表，记录订单配送情况
DROP TABLE IF EXISTS `wuliu`;
CREATE TABLE `wuliu`  (
  `order_id` int NOT NULL,
  `cons_phone` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `disp_id` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `deliver_time` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `ended` int NOT NULL DEFAULT 0,
  PRIMARY KEY (`order_id`) USING BTREE,
  UNIQUE INDEX `order_id`(`order_id`) USING BTREE,
  INDEX `cons_phone`(`cons_phone`) USING BTREE,
  INDEX `disp_id`(`disp_id`) USING BTREE,
  INDEX `deliver_time`(`deliver_time`) USING BTREE,
  INDEX `ended`(`ended`) USING BTREE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb3 ROW_FORMAT = DYNAMIC;

-- 初始化物流信息数据
INSERT INTO `wuliu` VALUES (2, '13912345678', 'D001', '25分钟', 0);

-- 已完成配送订单视图
DROP VIEW IF EXISTS `sended_order`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `sended_order` AS
SELECT oorder.order_id AS order_id,
       oorder.shop_name AS shop_name,
       oorder.order_money AS order_money,
       oorder.order_way AS order_way,
       oorder.cons_phone AS cons_phone,
       oorder.cons_name AS cons_name,
       oorder.cons_addre AS cons_addre,
       wuliu.disp_id AS disp_id,
       wuliu.deliver_time AS deliver_time,
       dispatcher.dispatcher_phone AS dispatcher_phone
FROM oorder
JOIN wuliu ON oorder.order_id = wuliu.order_id
JOIN dispatcher ON wuliu.disp_id = dispatcher.dispatcher_id
WHERE oorder.checked = 5;

-- 正在配送订单视图
DROP VIEW IF EXISTS `sending_order`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `sending_order` AS
SELECT oorder.order_id AS order_id,
       oorder.shop_name AS shop_name,
       oorder.order_money AS order_money,
       oorder.order_way AS order_way,
       oorder.cons_phone AS cons_phone,
       oorder.cons_name AS cons_name,
       oorder.cons_addre AS cons_addre,
       wuliu.disp_id AS disp_id,
       wuliu.deliver_time AS deliver_time,
       dispatcher.dispatcher_phone AS dispatcher_phone
FROM oorder
JOIN wuliu ON oorder.order_id = wuliu.order_id
JOIN dispatcher ON wuliu.disp_id = dispatcher.dispatcher_id
WHERE oorder.checked IN (1, 2, 3, 4);

-- 插入订单时更新订餐方式的计数
DROP TRIGGER IF EXISTS `order_insert`;
DELIMITER ;;
CREATE TRIGGER `order_insert` AFTER INSERT ON `oorder` FOR EACH ROW
BEGIN
  UPDATE orderway
  SET orderway.count = orderway.count + 1
  WHERE orderway.orderway_name = NEW.order_way;
END;;
DELIMITER ;

-- 插入订单时更新店铺销售量
DROP TRIGGER IF EXISTS `order_insert_sale`;
DELIMITER ;;
CREATE TRIGGER `order_insert_sale` AFTER INSERT ON `oorder` FOR EACH ROW
BEGIN
  UPDATE fastfood_shop
  SET fastfood_shop.m_sale_v = fastfood_shop.m_sale_v + 1
  WHERE fastfood_shop.shop_name = NEW.shop_name;
END;;
DELIMITER ;

-- 订单更新时，如更换订餐方式，更新对应统计
DROP TRIGGER IF EXISTS `order_update`;
DELIMITER ;;
CREATE TRIGGER `order_update` AFTER UPDATE ON `oorder` FOR EACH ROW
BEGIN
  IF NEW.order_way != OLD.order_way THEN
    UPDATE orderway SET orderway.count = orderway.count - 1 WHERE orderway.orderway_name = OLD.order_way;
    UPDATE orderway SET orderway.count = orderway.count + 1 WHERE orderway.orderway_name = NEW.order_way;
  END IF;
END;;
DELIMITER ;

-- 删除订单时同步减少订餐方式计数
DROP TRIGGER IF EXISTS `order_delete`;
DELIMITER ;;
CREATE TRIGGER `order_delete` AFTER DELETE ON `oorder` FOR EACH ROW
BEGIN
  UPDATE orderway
  SET orderway.count = orderway.count - 1
  WHERE orderway.orderway_name = OLD.order_way;
END;;
DELIMITER ;

-- 删除订单时减少店铺销售数量
DROP TRIGGER IF EXISTS `order_delete_sale`;
DELIMITER ;;
CREATE TRIGGER `order_delete_sale` AFTER DELETE ON `oorder` FOR EACH ROW
BEGIN
  UPDATE fastfood_shop
  SET fastfood_shop.m_sale_v = fastfood_shop.m_sale_v - 1
  WHERE fastfood_shop.shop_name = OLD.shop_name;
END;;
DELIMITER ;

-- 插入物流信息后将订单标记为“配送中”
DROP TRIGGER IF EXISTS `wuliu_insert`;
DELIMITER ;;
CREATE TRIGGER `wuliu_insert` AFTER INSERT ON `wuliu` FOR EACH ROW
BEGIN
  UPDATE oorder
  SET oorder.checked = 1
  WHERE oorder.order_id = NEW.order_id;
END;;
DELIMITER ;

SET FOREIGN_KEY_CHECKS = 1;
