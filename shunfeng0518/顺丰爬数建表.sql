-- 1.generate_mail_no: 存储生成的单号
DROP TABLE IF EXISTS `generate_mail_no`;
CREATE TABLE `generate_mail_no` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `yjhm` bigint(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=292257 DEFAULT CHARSET=utf8;

-- 2.mail_info: 存储运单信息
DROP TABLE IF EXISTS `mail_info`;
CREATE TABLE `mail_info` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `yjhm` bigint(20) NOT NULL,
  `locations` varchar(32) DEFAULT NULL,
  `locations_arrow` varchar(32) DEFAULT NULL,
  `product_name` varchar(32) DEFAULT NULL,
  `last_update_time` datetime DEFAULT NULL,
  `status` text,
  `crawler_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=90 DEFAULT CHARSET=utf8;

-- 3.mail_wuliu: 存储物流状态
DROP TABLE IF EXISTS `mail_wuliu`;
CREATE TABLE `mail_wuliu` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `yjhm` bigint(20) DEFAULT NULL,
  `time` datetime DEFAULT NULL,
  `status` text,
  `crawler_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 4.no_record_mail: 存储无物流信息的单号
DROP TABLE IF EXISTS `no_record_mail`;
CREATE TABLE `no_record_mail` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `yjhm` bigint(20) DEFAULT NULL,
  `crawler_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8;

-- 5.ori_ternimal: 记录每个点的编号
DROP TABLE IF EXISTS `ori_terminal`;
CREATE TABLE `ori_terminal` (
  `terminal_code` varchar(32) NOT NULL,
  `terminal_type` varchar(8) DEFAULT NULL,
  PRIMARY KEY (`terminal_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;