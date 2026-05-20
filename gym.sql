/*
Navicat MySQL Data Transfer

Source Server         : DB
Source Server Version : 80016
Source Host           : localhost:3306
Source Database       : gym

Target Server Type    : MYSQL
Target Server Version : 80016
File Encoding         : 65001

Date: 2022-12-19 23:48:33
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for coach
-- ----------------------------
DROP TABLE IF EXISTS `coach`;
CREATE TABLE `coach` (
  `cid` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(20) NOT NULL,
  `password` varchar(200) DEFAULT NULL,
  `cprofile` varchar(200) DEFAULT NULL,
  `Email` varchar(200) NOT NULL,
  `speciality` varchar(200) DEFAULT NULL,
  `sex` int(11) DEFAULT NULL,
  PRIMARY KEY (`cid`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of coach
-- ----------------------------
INSERT INTO `coach` VALUES ('1', 'Coach', '$2b$12$raojK3XvkkXqnh3x.3mzPekjjo5sgn0b3KG52d/8PFsNpkiQNN5gm', '../static/coachProfile/default_none.jpg', 'coach1@example.com', 'all', '0');
INSERT INTO `coach` VALUES ('2', 'Tommy', '$2b$12$JFF86F97Xgcl02KgqeP5kerRRD1bK2iB6xf7kdKnjSm3pF95vhmwy', '../static/coachProfile/default_male.jpg', 'coach2@example.com', 'strength', '1');
INSERT INTO `coach` VALUES ('3', 'Jenny', '$2b$12$hf8zj8lfm8sagM6fy3yhSO7GQuHBAnwWbBdCUIJ5FVBj97jXzrB0y', '../static/coachProfile/default_female.jpg', 'coach3@example.com', 'yoga', '2');
INSERT INTO `coach` VALUES ('6', 'test', '$2b$12$VpcF2ZwYC4asrmJ4ecScweFNGSz09LbYKTB2zgylcn/L3TaSi.s96', '../static/coachProfile/test.jpg', 'coach4@example.com', 'fitting', '1');

-- ----------------------------
-- Table structure for connect
-- ----------------------------
DROP TABLE IF EXISTS `connect`;
CREATE TABLE `connect` (
  `num` int(11) NOT NULL AUTO_INCREMENT,
  `id` int(11) NOT NULL,
  `cid` int(11) NOT NULL,
  `courseid` int(11) NOT NULL,
  PRIMARY KEY (`num`),
  KEY `id` (`id`),
  KEY `cid` (`cid`),
  KEY `courseid` (`courseid`),
  CONSTRAINT `connect_ibfk_1` FOREIGN KEY (`id`) REFERENCES `customer` (`id`),
  CONSTRAINT `connect_ibfk_2` FOREIGN KEY (`cid`) REFERENCES `coach` (`cid`),
  CONSTRAINT `connect_ibfk_3` FOREIGN KEY (`courseid`) REFERENCES `course` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of connect
-- ----------------------------
INSERT INTO `connect` VALUES ('2', '15', '2', '2');
INSERT INTO `connect` VALUES ('3', '15', '3', '3');
INSERT INTO `connect` VALUES ('5', '15', '3', '5');
INSERT INTO `connect` VALUES ('7', '15', '1', '1');
INSERT INTO `connect` VALUES ('10', '13', '3', '4');

-- ----------------------------
-- Table structure for course
-- ----------------------------
DROP TABLE IF EXISTS `course`;
CREATE TABLE `course` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cid` int(11) NOT NULL,
  `name` varchar(20) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `courseProfile` varchar(200) DEFAULT NULL,
  `start` datetime DEFAULT NULL,
  `end` datetime DEFAULT NULL,
  `video` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `cid` (`cid`),
  CONSTRAINT `course_ibfk_1` FOREIGN KEY (`cid`) REFERENCES `coach` (`cid`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of course
-- ----------------------------
INSERT INTO `course` VALUES ('1', '1', 'Fitting overall', 'This is a course for all members! Join me to experience the fun of gym exercises and get MUSCLES!', '../static/Course/cover/Coach20221217_204532.jpg', '2022-12-17 20:44:12', '2022-12-17 22:00:12', '../static/Course/video/_Compressed_Coach20221217_204532.mp4');
INSERT INTO `course` VALUES ('2', '2', 'Strength class', 'Join me to work on your strength! This course is for those who want to improve on their strength.', '../static/Course/cover/Tommy20221217_204850.jpg', '2022-12-18 10:45:12', '2022-12-18 12:45:12', '../static/Course/video/_Compressed_Tommy20221217_204850.mp4');
INSERT INTO `course` VALUES ('3', '2', 'Mobile cycle', 'This is a course for mobile cycling: the most popular after-work exercise! So the time period is set after work. Don\'t forget to come after work!', '../static/Course/cover/Tommy20221217_205244.jpg', '2022-12-19 20:30:12', '2022-12-19 21:45:12', '../static/Course/video/Tommy20221217_205244.mp4');
INSERT INTO `course` VALUES ('4', '3', 'Swimming junior', 'Want to go to the beach with friends at summer? Join me this winter holiday! Here we will teach basic skills of swimming. ', '../static/Course/cover/Jenny20221217_205454.jpg', '2022-12-18 15:45:12', '2022-12-18 17:45:12', '../static/Course/video/_Compressed_Jenny20221217_205454.mp4');
INSERT INTO `course` VALUES ('5', '3', 'Yoga master', 'Want to improve your yoga? Join me here. We will help you to grow higher skills of yoga and relax yourself after a long day of working.', '../static/Course/cover/Jenny20221217_205854.jpg', '2022-12-20 20:00:12', '2022-12-20 22:00:12', '../static/Course/video/_Compressed_Jenny20221217_205854.mp4');

-- ----------------------------
-- Table structure for customer
-- ----------------------------
DROP TABLE IF EXISTS `customer`;
CREATE TABLE `customer` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(20) NOT NULL,
  `password` varchar(200) DEFAULT NULL,
  `profile` varchar(200) DEFAULT NULL,
  `Email` varchar(200) NOT NULL,
  `status` int(11) DEFAULT NULL,
  `log` int(11) DEFAULT NULL,
  `sex` int(11) DEFAULT NULL,
  `posts` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of customer
-- ----------------------------
INSERT INTO `customer` VALUES ('8', 'demo', '$2b$12$OTBnXFYSzYvjmxoHV4FSVu9gJ5tQ1/RXZ3ewF91Rtl8VsMTnviqpi', '../static/customerProfile/default_none.jpg', 'customer1@example.com', '1', '0', '0', '0');
INSERT INTO `customer` VALUES ('9', 'Female', '$2b$12$u6uXzkssfEP1YKocMEKCwOi0WxbKqVGo3sMkE86/1l4HHVTV.AfS2', '../static/customerProfile/default_female.jpg', 'customer2@example.com', '0', '0', '2', '0');
INSERT INTO `customer` VALUES ('13', 'test', '$2b$12$UzQirhqtyx9Yy60vjMq5vOOCes80VU6gGn7PVA3XkD8VriKWZtntK', '../static/customerProfile/default_male.jpg', 'customer3@example.com', '1', '0', '1', '2');
INSERT INTO `customer` VALUES ('15', 'DemoUser', '$2b$12$EvdvjI0hVDeHlFyPcskKIeQX0rMg3VGyRUBnk2ExD68g9GCUOq9k2', '../static/customerProfile/DemoUser.jpeg', 'customer4@example.com', '1', '0', '1', '2');

-- ----------------------------
-- Table structure for health
-- ----------------------------
DROP TABLE IF EXISTS `health`;
CREATE TABLE `health` (
  `uid` int(11) NOT NULL,
  `birthday` date DEFAULT NULL,
  `height` int(11) DEFAULT NULL,
  `weight` int(11) DEFAULT NULL,
  `aim_weight` int(11) DEFAULT NULL,
  `prefer` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`uid`),
  CONSTRAINT `health_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `customer` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of health
-- ----------------------------
INSERT INTO `health` VALUES ('8', '2022-12-09', '0', '0', '0', 'fitting');
INSERT INTO `health` VALUES ('9', '2022-12-09', '0', '0', '0', 'yoga');
INSERT INTO `health` VALUES ('13', '2022-12-09', '0', '0', '0', 'strength');
INSERT INTO `health` VALUES ('15', '2020-01-14', '180', '65', '60', 'swimming');

-- ----------------------------
-- Table structure for manager
-- ----------------------------
DROP TABLE IF EXISTS `manager`;
CREATE TABLE `manager` (
  `aid` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(20) NOT NULL,
  `password` varchar(200) DEFAULT NULL,
  `Email` varchar(200) NOT NULL,
  `log` int(11) DEFAULT NULL,
  PRIMARY KEY (`aid`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of manager
-- ----------------------------
INSERT INTO `manager` VALUES ('1', 'Admin', '$2b$12$FBgvzU.bUNQZ9DkKqGCxou26FxKBfuor4IgNKo5iiQ7Uq1Glzii1y', 'admin@example.com', '0');
INSERT INTO `manager` VALUES ('2', 'Manager', '$2b$12$OByzHUoNiubLvrEaI6xFw.243FSBoZrmtB3Xx52h1fUJfo5ESZYfS', 'manager@example.com', '0');

-- ----------------------------
-- Table structure for post
-- ----------------------------
DROP TABLE IF EXISTS `post`;
CREATE TABLE `post` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uid` int(11) NOT NULL,
  `photo` varchar(200) DEFAULT NULL,
  `description` varchar(200) DEFAULT NULL,
  `tag` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `uid` (`uid`),
  CONSTRAINT `post_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `customer` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of post
-- ----------------------------
INSERT INTO `post` VALUES ('1', '13', '../static/post/test20221216_193109.jpg', 'Hello everyone! this is my first day at workout gym.', 'first');
INSERT INTO `post` VALUES ('2', '13', '../static/post/test20221216_193246.jpg', 'This is my second day at workout gym. This is a test of 200 charatcer up limit of the blog. AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', 'Daily');
INSERT INTO `post` VALUES ('3', '15', '../static/post/DemoUser20221216_193331.jpg', 'I am posting a blog.', 'first');
INSERT INTO `post` VALUES ('6', '15', '../static/post/DemoUser20221217_104537.jpeg', 'Good night everyone! Work hard tomorrow.', 'Night');
