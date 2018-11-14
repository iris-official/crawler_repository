DROP TABLE IF EXISTS `kd100_mail_info`;
CREATE TABLE `kd100_mail_info` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `yjhm` varchar(32) NOT NULL,
  `locations` varchar(32) DEFAULT NULL,
  `locations_arrow` varchar(32) DEFAULT NULL,
  `product_name` varchar(32) DEFAULT NULL,
  `last_update_time` varchar(32) DEFAULT NULL,
  `status` varchar(500) DEFAULT NULL,
  `crawler_time` varchar(32) DEFAULT NULL,
  `add_do` varchar(32) DEFAULT NULL,
  `add_flag` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2722 DEFAULT CHARSET=utf8;