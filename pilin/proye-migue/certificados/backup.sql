-- MySQL dump 10.13  Distrib 8.0.42, for Linux (x86_64)
--
-- Host: localhost    Database: aplicacion
-- ------------------------------------------------------
-- Server version	8.0.42-0ubuntu0.24.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add user',4,'add_user'),(14,'Can change user',4,'change_user'),(15,'Can delete user',4,'delete_user'),(16,'Can view user',4,'view_user'),(17,'Can add content type',5,'add_contenttype'),(18,'Can change content type',5,'change_contenttype'),(19,'Can delete content type',5,'delete_contenttype'),(20,'Can view content type',5,'view_contenttype'),(21,'Can add session',6,'add_session'),(22,'Can change session',6,'change_session'),(23,'Can delete session',6,'delete_session'),(24,'Can view session',6,'view_session'),(25,'Can add servidor',7,'add_servidor'),(26,'Can change servidor',7,'change_servidor'),(27,'Can delete servidor',7,'delete_servidor'),(28,'Can view servidor',7,'view_servidor'),(29,'Can add usuario',8,'add_usuario'),(30,'Can change usuario',8,'change_usuario'),(31,'Can delete usuario',8,'delete_usuario'),(32,'Can view usuario',8,'view_usuario'),(33,'Can add contador intentos',9,'add_contadorintentos'),(34,'Can change contador intentos',9,'change_contadorintentos'),(35,'Can delete contador intentos',9,'delete_contadorintentos'),(36,'Can view contador intentos',9,'view_contadorintentos'),(37,'Can add captcha store',10,'add_captchastore'),(38,'Can change captcha store',10,'change_captchastore'),(39,'Can delete captcha store',10,'delete_captchastore'),(40,'Can view captcha store',10,'view_captchastore');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `captcha_captchastore`
--

DROP TABLE IF EXISTS `captcha_captchastore`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `captcha_captchastore` (
  `id` int NOT NULL AUTO_INCREMENT,
  `challenge` varchar(32) NOT NULL,
  `response` varchar(32) NOT NULL,
  `hashkey` varchar(40) NOT NULL,
  `expiration` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `hashkey` (`hashkey`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `captcha_captchastore`
--

LOCK TABLES `captcha_captchastore` WRITE;
/*!40000 ALTER TABLE `captcha_captchastore` DISABLE KEYS */;
INSERT INTO `captcha_captchastore` VALUES (1,'PWFF','pwff','ae97a3bb9219fa5b695880442d07e6003afb0a57','2025-05-07 05:58:36.276722'),(2,'OBNI','obni','2ac9e85d2c8f6c61ed5675062b875c2c07cf8690','2025-05-07 05:58:40.322763'),(3,'GWDH','gwdh','ae07bcd9ac169f246506f398b7a34eaebf09d51e','2025-05-07 06:01:32.423420'),(4,'DVTJ','dvtj','cd54cc020513773023dd9b0f25b5fb4ebcd20f7e','2025-05-07 06:02:17.483794');
/*!40000 ALTER TABLE `captcha_captchastore` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'auth','user'),(10,'captcha','captchastore'),(5,'contenttypes','contenttype'),(9,'servidores','contadorintentos'),(7,'servidores','servidor'),(8,'servidores','usuario'),(6,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2025-05-02 19:57:40.960590'),(2,'auth','0001_initial','2025-05-02 19:57:44.853463'),(3,'admin','0001_initial','2025-05-02 19:57:45.973424'),(4,'admin','0002_logentry_remove_auto_add','2025-05-02 19:57:46.045520'),(5,'admin','0003_logentry_add_action_flag_choices','2025-05-02 19:57:46.111934'),(6,'contenttypes','0002_remove_content_type_name','2025-05-02 19:57:46.845289'),(7,'auth','0002_alter_permission_name_max_length','2025-05-02 19:57:47.353252'),(8,'auth','0003_alter_user_email_max_length','2025-05-02 19:57:47.508086'),(9,'auth','0004_alter_user_username_opts','2025-05-02 19:57:47.579264'),(10,'auth','0005_alter_user_last_login_null','2025-05-02 19:57:47.979212'),(11,'auth','0006_require_contenttypes_0002','2025-05-02 19:57:48.001603'),(12,'auth','0007_alter_validators_add_error_messages','2025-05-02 19:57:48.145093'),(13,'auth','0008_alter_user_username_max_length','2025-05-02 19:57:48.768668'),(14,'auth','0009_alter_user_last_name_max_length','2025-05-02 19:57:49.166869'),(15,'auth','0010_alter_group_name_max_length','2025-05-02 19:57:49.306704'),(16,'auth','0011_update_proxy_permissions','2025-05-02 19:57:49.377694'),(17,'auth','0012_alter_user_first_name_max_length','2025-05-02 19:57:49.807700'),(18,'servidores','0001_initial','2025-05-02 19:57:50.003016'),(19,'sessions','0001_initial','2025-05-02 19:57:50.259770'),(20,'servidores','0002_usuario_alter_servidor_id','2025-05-07 02:12:45.686750'),(21,'servidores','0003_contadorintentos','2025-05-07 02:12:45.830181'),(22,'servidores','0004_remove_usuario_id_usuario_chat_id_and_more','2025-05-07 05:06:30.789447'),(23,'captcha','0001_initial','2025-05-07 05:53:17.195209'),(24,'captcha','0002_alter_captchastore_id','2025-05-07 05:53:17.243634');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('2b7b7wtqn43urzslqx1802x0kc292yjl','eyJ1c3VhcmlvX3RtcCI6ImFkbWluIiwidG9rZW5fMmZhIjoid0VuYjdVU1dzUFpNcmp4cSIsImV4cGlyYV8yZmEiOjE3NDk2MDIyMDUuNjE5MzYzfQ:1uP9QU:vJbdxTetOHq29fmzCdfDguCBkkFRMPHA60zck-3u1kk','2025-06-25 00:34:46.196176'),('6wc9uirg847pcunf372v6kpksqahoh7k','eyJ1c3VhcmlvIjoiYWRtaW4ifQ:1uCXxc:iNgnaP1Afy9BRoCw8iAoegGfhun8ZxjGy62crgeGwM0','2025-05-21 06:08:52.359270'),('bbn1a2fvw0jlrym98xb90iap6tpgdy34','eyJzZXJ2aWRvcl9pZCI6Mn0:1uAwm5:94s2hTYeAv9IcBX9ESf4OuRPj0nRDCT9WNG84zdOyWM','2025-05-16 20:14:21.783110'),('ly6n8rxj7p733f3tikhvcabhhjajagq7','eyJ1c3VhcmlvIjoiYWRtaW4iLCJzZXJ2aWRvcl9pZCI6IjE5Mi0xNjgtMS03N190aGl6enkifQ:1uLGKi:JJIjv2bcFZDvMa6h8_0sxwV1gwX-O0b-CIyaLkSJEak','2025-06-14 07:08:44.075281'),('x1y9hdxiwsc0skbl2vo05gqa7eby0jz8','eyJ1c3VhcmlvIjoiYWRtaW4ifQ:1uGYso:QtCg1O0Kx42c2sGD6vrE1QK_S6FTZoXB-Sp-dt8YDww','2025-06-01 07:56:30.748599');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `servidores_contadorintentos`
--

DROP TABLE IF EXISTS `servidores_contadorintentos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `servidores_contadorintentos` (
  `ip` char(39) NOT NULL,
  `contador` int unsigned NOT NULL,
  `ultimo_intento` datetime(6) NOT NULL,
  PRIMARY KEY (`ip`),
  CONSTRAINT `servidores_contadorintentos_chk_1` CHECK ((`contador` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `servidores_contadorintentos`
--

LOCK TABLES `servidores_contadorintentos` WRITE;
/*!40000 ALTER TABLE `servidores_contadorintentos` DISABLE KEYS */;
INSERT INTO `servidores_contadorintentos` VALUES ('10.50.2.66',3,'2025-06-11 00:34:45.451206'),('192.168.1.64',1,'2025-05-18 07:56:17.796037'),('192.168.1.69',1,'2025-05-07 03:41:14.667882'),('192.168.1.72',3,'2025-05-31 07:04:45.146918');
/*!40000 ALTER TABLE `servidores_contadorintentos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `servidores_servidor`
--

DROP TABLE IF EXISTS `servidores_servidor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `servidores_servidor` (
  `id` varchar(255) NOT NULL,
  `host_cifrado` longblob NOT NULL,
  `usuario_cifrado` longblob NOT NULL,
  `contrasena_cifrada` longblob NOT NULL,
  `fecha_registro` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `servidores_servidor`
--

LOCK TABLES `servidores_servidor` WRITE;
/*!40000 ALTER TABLE `servidores_servidor` DISABLE KEYS */;
INSERT INTO `servidores_servidor` VALUES ('192-168-1-77_thizzy',_binary 'gAAAAABoOqr1Qe0nWsnfasRxL3yZ3608p2gDkA4RT4Pr6zWBOcRwm8mFiZzpKMnZIJIs-k4fhMdrANNl0e3iEBsMTQ6C2SEl5A==',_binary 'gAAAAABoOqr10_GcCIsJGwXvswjVW3cwo2-YvfGILHl5fY1EaEaiinIDL3u54Mdouz-e1fP1libjcjiBNR_FwcN-PMo4C-XHzA==',_binary 'gAAAAABoOqr1eCKUc_8-aKFGeW-Gn6H1YjtPbBj33iiHyIjmw3HQCs1ZF7h_gHpowg_GoP3lGOQ-tDiCvJS6tTlQx4U1rjq_Zg==','2025-05-31 07:08:37.267405'),('2',_binary 'gAAAAABoFSedF03zj6X0MR6Fu2TQxYI3gEHfLWLoHwY93ExR_0MQQAkKbhze2hFP2fT8Gsq7Jr6z8XoTG01NtCy0zUWKi56mqQ==',_binary 'gAAAAABoFSed1tAsVzmPAmlYmA1Bu-o2v-g_9B5yi6TKXRvWbhmc1xSjkcSo4_fE7z7JyWx2h-V_7sewBTWZvXW3kiiIQOBGIA==',_binary 'gAAAAABoFSed-S8CsqEbjL1pQTxO7hLD7UC3PTr_pbovgC1ckKHRaGyDTRljwv62dEyFYMt46M8yJnOWFTuCjjn1JJrtLQg4jw==','2025-05-02 20:14:21.720919');
/*!40000 ALTER TABLE `servidores_servidor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `servidores_usuario`
--

DROP TABLE IF EXISTS `servidores_usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `servidores_usuario` (
  `nombre_usuario` varchar(150) NOT NULL,
  `contrasena_sha256` varchar(255) NOT NULL,
  `chat_id` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`nombre_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `servidores_usuario`
--

LOCK TABLES `servidores_usuario` WRITE;
/*!40000 ALTER TABLE `servidores_usuario` DISABLE KEYS */;
INSERT INTO `servidores_usuario` VALUES ('admin','$6$wLn3hfSJdxalxrpH$2151b33e1b2d4177c6e98fc8cea88ffff5f5d2ba6e893d585d3cb5003f10179069c719e6bf2c7f3e5547132997988ef9afbdc3ca73777e6ca51fb3d7c41a9a70','7165229658');
/*!40000 ALTER TABLE `servidores_usuario` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-06-11  4:35:43
