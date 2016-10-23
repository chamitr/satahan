-- MySQL dump 10.13  Distrib 5.6.23, for Win64 (x86_64)
--
-- Host: localhost    Database: satahan$satahan
-- ------------------------------------------------------
-- Server version	5.5.42-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `attachment`
--

DROP TABLE IF EXISTS `attachment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `attachment` (
  `idattachment` int(11) NOT NULL AUTO_INCREMENT,
  `idnote` int(11) NOT NULL,
  `filename` tinytext NOT NULL,
  PRIMARY KEY (`idattachment`),
  KEY `kf_noteattachment_idx` (`idnote`),
  CONSTRAINT `kf_attachmentnote` FOREIGN KEY (`idnote`) REFERENCES `note` (`idnote`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `comment`
--

DROP TABLE IF EXISTS `comment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `comment` (
  `idcomment` int(11) NOT NULL AUTO_INCREMENT,
  `text` text NOT NULL,
  `iduser` int(11) NOT NULL,
  `createdatetime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `idnote` int(11) NOT NULL,
  PRIMARY KEY (`idcomment`),
  KEY `fk_comment_user_idx` (`iduser`),
  KEY `fk_comment_satahan_idx` (`idnote`),
  CONSTRAINT `fk_comment_note` FOREIGN KEY (`idnote`) REFERENCES `note` (`idnote`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_comment_user` FOREIGN KEY (`iduser`) REFERENCES `user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `note`
--

DROP TABLE IF EXISTS `note`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `note` (
  `idnote` int(11) NOT NULL AUTO_INCREMENT,
  `title` tinytext CHARACTER SET utf8 NOT NULL,
  `text` text CHARACTER SET utf8 NOT NULL,
  `iduser` int(11) NOT NULL DEFAULT '0',
  `createdatetime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `comments_count` int(11) NOT NULL DEFAULT '0',
  `published` tinyint(4) NOT NULL DEFAULT '0',
  `attachment_count` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`idnote`),
  KEY `fk_user_idx` (`iduser`),
  CONSTRAINT `fk_user` FOREIGN KEY (`iduser`) REFERENCES `user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=929 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `notetag`
--

DROP TABLE IF EXISTS `notetag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `notetag` (
  `idtag` int(11) NOT NULL,
  `idnote` int(11) NOT NULL,
  PRIMARY KEY (`idtag`,`idnote`),
  KEY `fk_satahan_idx` (`idnote`),
  CONSTRAINT `fk_note` FOREIGN KEY (`idnote`) REFERENCES `note` (`idnote`) ON DELETE CASCADE ON UPDATE NO ACTION,
  CONSTRAINT `fk_tag` FOREIGN KEY (`idtag`) REFERENCES `tag` (`idtag`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tag`
--

DROP TABLE IF EXISTS `tag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tag` (
  `idtag` int(11) NOT NULL AUTO_INCREMENT,
  `tagname` varchar(75) NOT NULL,
  `idtaggroup` int(11) NOT NULL,
  `tagpage` varchar(75) DEFAULT NULL,
  PRIMARY KEY (`idtag`),
  KEY `fk_taggroup_idx` (`idtaggroup`),
  CONSTRAINT `fk_taggroup` FOREIGN KEY (`idtaggroup`) REFERENCES `taggroup` (`idtaggroup`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=1037 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `taggroup`
--

DROP TABLE IF EXISTS `taggroup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `taggroup` (
  `idtaggroup` int(11) NOT NULL AUTO_INCREMENT,
  `taggroupname` varchar(75) NOT NULL,
  PRIMARY KEY (`idtaggroup`),
  UNIQUE KEY `taggroupname_UNIQUE` (`taggroupname`)
) ENGINE=InnoDB AUTO_INCREMENT=63 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(120) NOT NULL,
  `password` varchar(60) DEFAULT NULL,
  `username` varchar(50) NOT NULL,
  `active` tinyint(4) NOT NULL DEFAULT '0',
  `confirmed_at` datetime DEFAULT NULL,
  `is_admin` tinyint(4) NOT NULL DEFAULT '0',
  `social_id` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `social_id_UNIQUE` (`social_id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `usersettings`
--

DROP TABLE IF EXISTS `usersettings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `usersettings` (
  `iduser` int(11) NOT NULL,
  `idtaggroup_def` int(11) DEFAULT NULL,
  `admin_points` int(11) NOT NULL DEFAULT '10',
  PRIMARY KEY (`iduser`),
  CONSTRAINT `fk_setting_user` FOREIGN KEY (`iduser`) REFERENCES `user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `usertaggroup`
--

DROP TABLE IF EXISTS `usertaggroup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `usertaggroup` (
  `iduser` int(11) NOT NULL,
  `idtaggroup` int(11) NOT NULL,
  PRIMARY KEY (`iduser`,`idtaggroup`),
  KEY `fk_taggroup_idx` (`idtaggroup`),
  CONSTRAINT `fk_usertaggroup` FOREIGN KEY (`idtaggroup`) REFERENCES `taggroup` (`idtaggroup`) ON DELETE CASCADE ON UPDATE NO ACTION,
  CONSTRAINT `kf_user` FOREIGN KEY (`iduser`) REFERENCES `user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-10-23 20:19:02
