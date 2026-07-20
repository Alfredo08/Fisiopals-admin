-- MySQL dump 10.13  Distrib 8.0.34, for macos13 (x86_64)
--
-- Host: localhost    Database: bd_fisiopals
-- ------------------------------------------------------
-- Server version	8.3.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `administradores`
--

DROP TABLE IF EXISTS `administradores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `administradores` (
  `id_administrador` int NOT NULL AUTO_INCREMENT,
  `nombre_completo` varchar(200) NOT NULL,
  `correo` varchar(200) NOT NULL,
  `password` varchar(400) NOT NULL,
  PRIMARY KEY (`id_administrador`),
  UNIQUE KEY `correo` (`correo`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `administradores`
--

LOCK TABLES `administradores` WRITE;
/*!40000 ALTER TABLE `administradores` DISABLE KEYS */;
INSERT INTO `administradores` VALUES (1,'Alfredo Salazar','alfredo@salazar.com','$2b$12$7VsQ67mGmsuWLFCkyP2Ore1wedQkFfv/j8nEljQkOO6tOWjq61aF2'),(2,'Monica Naranjo','monica@nRnjo.com','$2b$12$u995Ld42thB/.gFYd6O84ePUfwwmtz7nvL5osRtMDMjTLKQarsMdG');
/*!40000 ALTER TABLE `administradores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `clientes`
--

DROP TABLE IF EXISTS `clientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `clientes` (
  `id_cliente` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `correo` varchar(200) NOT NULL,
  `telefono` varchar(20) NOT NULL,
  `saldo` decimal(10,2) NOT NULL DEFAULT '0.00',
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_cliente`),
  UNIQUE KEY `correo` (`correo`),
  UNIQUE KEY `telefono` (`telefono`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clientes`
--

LOCK TABLES `clientes` WRITE;
/*!40000 ALTER TABLE `clientes` DISABLE KEYS */;
INSERT INTO `clientes` VALUES (1,'Julieta Salazar','julieta@salazar.com','8441201021',-1260.00,'2026-07-01 17:32:49','2026-07-09 14:31:35'),(2,'Ernesto Charles','ernesto@charles.com','8442716234',-950.00,'2026-07-01 17:33:25','2026-07-09 14:21:44'),(3,'Roberto López','roberto@lopez.com','8448872394',0.00,'2026-07-01 17:33:46','2026-07-01 17:33:46'),(4,'Alfredo Salazar','alfredo@salazar.com','8442771792',0.00,'2026-07-01 18:09:58','2026-07-20 13:57:09'),(5,'Mariana Rodriguez','mariana@rodriguez.com','81726362123',500.00,'2026-07-09 13:57:21','2026-07-20 13:58:43'),(6,'Roger Alejandro','roger@alejandro.com','8726374821',0.00,'2026-07-14 11:42:02','2026-07-14 11:42:02'),(7,'Liliana Rodrìguez','liliana@rodriguez.com','1231231232',0.00,'2026-07-20 13:29:37','2026-07-20 13:29:37'),(8,'Juve Guzmán','juve@guzman.com','726354672',0.00,'2026-07-20 15:23:05','2026-07-20 15:23:05');
/*!40000 ALTER TABLE `clientes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `datos_clinicos`
--

DROP TABLE IF EXISTS `datos_clinicos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `datos_clinicos` (
  `id_dato_clinico` int NOT NULL AUTO_INCREMENT,
  `fecha` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `retroalimentacion` varchar(500) NOT NULL,
  `palpacion_examen` varchar(500) NOT NULL,
  `trabajo_sesion` varchar(500) NOT NULL,
  `objetivos` varchar(500) NOT NULL,
  `trabajo_casa` varchar(500) NOT NULL,
  `id_paciente` int NOT NULL,
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_dato_clinico`),
  KEY `id_paciente` (`id_paciente`),
  CONSTRAINT `datos_clinicos_ibfk_1` FOREIGN KEY (`id_paciente`) REFERENCES `pacientes` (`id_paciente`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `datos_clinicos`
--

LOCK TABLES `datos_clinicos` WRITE;
/*!40000 ALTER TABLE `datos_clinicos` DISABLE KEYS */;
INSERT INTO `datos_clinicos` VALUES (1,'2026-07-06 00:00:00','Buen avance','Buen avance','Buen avance','Buen avance','Buen avance',1,'2026-07-06 13:51:14','2026-07-06 13:51:14'),(2,'2026-07-07 00:00:00','Mejoras','Mejoras',' Mejoras 2','Mejoras 2','Mejoras 2',1,'2026-07-06 13:57:33','2026-07-20 10:49:08'),(3,'2026-07-09 00:00:00','d sdf sdf sdf ','ssdf sdf sdf sd',' sdf sdf sdf sdf','sdf sdf sdf ','sdf sdf sdf',4,'2026-07-09 14:02:30','2026-07-09 14:02:30'),(4,'2026-07-20 00:00:00','ha esta bien','dolor en elcuello ','laser bla bla bal ','mejorar','ejercicio pasto ',8,'2026-07-20 13:32:34','2026-07-20 14:04:13');
/*!40000 ALTER TABLE `datos_clinicos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orden_productos`
--

DROP TABLE IF EXISTS `orden_productos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orden_productos` (
  `id_orden_producto` int NOT NULL AUTO_INCREMENT,
  `id_orden` int NOT NULL,
  `id_producto` int NOT NULL,
  `cantidad` int NOT NULL DEFAULT '1',
  `precio_unitario` decimal(10,2) NOT NULL,
  `subtotal` decimal(10,2) NOT NULL,
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_orden_producto`),
  KEY `id_orden` (`id_orden`),
  KEY `id_producto` (`id_producto`),
  CONSTRAINT `orden_productos_ibfk_1` FOREIGN KEY (`id_orden`) REFERENCES `ordenes` (`id_orden`) ON DELETE CASCADE,
  CONSTRAINT `orden_productos_ibfk_2` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`),
  CONSTRAINT `orden_productos_chk_1` CHECK ((`cantidad` > 0))
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orden_productos`
--

LOCK TABLES `orden_productos` WRITE;
/*!40000 ALTER TABLE `orden_productos` DISABLE KEYS */;
INSERT INTO `orden_productos` VALUES (8,7,2,1,10.00,10.00,'2026-07-09 14:05:49'),(9,13,1,1,120.00,120.00,'2026-07-09 14:21:44'),(10,14,2,3,10.00,30.00,'2026-07-09 14:22:42'),(11,15,1,1,120.00,120.00,'2026-07-09 14:31:35'),(12,15,3,2,170.00,340.00,'2026-07-09 14:31:35'),(13,24,3,1,170.00,170.00,'2026-07-20 11:09:38'),(14,25,3,1,170.00,170.00,'2026-07-20 11:10:04'),(15,26,2,1,10.00,10.00,'2026-07-20 11:10:23'),(16,26,3,1,170.00,170.00,'2026-07-20 11:10:23'),(17,27,3,1,170.00,170.00,'2026-07-20 13:35:45');
/*!40000 ALTER TABLE `orden_productos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orden_servicios`
--

DROP TABLE IF EXISTS `orden_servicios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orden_servicios` (
  `id_orden_servicio` int NOT NULL AUTO_INCREMENT,
  `id_orden` int NOT NULL,
  `id_servicio` int NOT NULL,
  `cantidad` int NOT NULL DEFAULT '1',
  `precio_unitario` decimal(10,2) NOT NULL,
  `subtotal` decimal(10,2) NOT NULL,
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_orden_servicio`),
  KEY `id_orden` (`id_orden`),
  KEY `id_servicio` (`id_servicio`),
  CONSTRAINT `orden_servicios_ibfk_1` FOREIGN KEY (`id_orden`) REFERENCES `ordenes` (`id_orden`) ON DELETE CASCADE,
  CONSTRAINT `orden_servicios_ibfk_2` FOREIGN KEY (`id_servicio`) REFERENCES `servicios` (`id_servicio`),
  CONSTRAINT `orden_servicios_chk_1` CHECK ((`cantidad` > 0))
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orden_servicios`
--

LOCK TABLES `orden_servicios` WRITE;
/*!40000 ALTER TABLE `orden_servicios` DISABLE KEYS */;
INSERT INTO `orden_servicios` VALUES (7,5,2,1,250.00,250.00,'2026-07-06 13:37:36'),(8,6,1,1,800.00,800.00,'2026-07-09 14:05:35'),(9,7,1,1,800.00,800.00,'2026-07-09 14:05:49'),(10,8,1,1,800.00,800.00,'2026-07-09 14:07:17'),(11,9,1,1,800.00,800.00,'2026-07-09 14:14:38'),(12,10,3,1,600.00,600.00,'2026-07-09 14:15:47'),(13,11,1,1,700.00,700.00,'2026-07-09 14:17:05'),(14,13,3,1,600.00,600.00,'2026-07-09 14:21:43'),(15,13,2,1,250.00,250.00,'2026-07-09 14:21:43'),(16,14,1,1,800.00,800.00,'2026-07-09 14:22:42'),(17,15,1,1,800.00,800.00,'2026-07-09 14:31:35'),(18,16,1,2,800.00,1600.00,'2026-07-14 12:39:53'),(19,17,1,1,800.00,800.00,'2026-07-14 12:50:04'),(20,18,3,1,600.00,600.00,'2026-07-14 12:53:01'),(21,19,2,1,250.00,250.00,'2026-07-14 13:53:36'),(22,20,2,1,250.00,250.00,'2026-07-14 14:31:39'),(23,21,1,1,800.00,800.00,'2026-07-14 14:32:08'),(24,22,2,1,250.00,250.00,'2026-07-14 14:33:06'),(25,23,1,1,800.00,800.00,'2026-07-20 11:08:25'),(26,24,1,1,800.00,800.00,'2026-07-20 11:09:38'),(27,25,3,1,600.00,600.00,'2026-07-20 11:10:04'),(28,26,3,1,600.00,600.00,'2026-07-20 11:10:23'),(29,27,1,1,800.00,800.00,'2026-07-20 13:35:45'),(30,28,2,1,250.00,250.00,'2026-07-20 13:43:09'),(31,29,3,1,600.00,600.00,'2026-07-20 13:46:31'),(32,30,3,1,600.00,600.00,'2026-07-20 13:57:09'),(33,30,2,1,250.00,250.00,'2026-07-20 13:57:09');
/*!40000 ALTER TABLE `orden_servicios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ordenes`
--

DROP TABLE IF EXISTS `ordenes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ordenes` (
  `id_orden` int NOT NULL AUTO_INCREMENT,
  `id_paciente` int DEFAULT NULL,
  `nombre_comprador` varchar(100) DEFAULT NULL,
  `estado` enum('pendiente','pagada','cancelada') NOT NULL DEFAULT 'pendiente',
  `total` decimal(10,2) NOT NULL DEFAULT '0.00',
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `saldo_aplicado` decimal(10,2) NOT NULL DEFAULT '0.00',
  `monto_pagado` decimal(10,2) NOT NULL DEFAULT '0.00',
  `estado_pago` enum('pendiente','parcial','pagada') NOT NULL DEFAULT 'pendiente',
  PRIMARY KEY (`id_orden`),
  KEY `id_paciente` (`id_paciente`),
  CONSTRAINT `ordenes_ibfk_1` FOREIGN KEY (`id_paciente`) REFERENCES `pacientes` (`id_paciente`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ordenes`
--

LOCK TABLES `ordenes` WRITE;
/*!40000 ALTER TABLE `ordenes` DISABLE KEYS */;
INSERT INTO `ordenes` VALUES (5,1,NULL,'pagada',250.00,'2026-07-06 13:37:36','2026-07-06 13:37:36',0.00,0.00,'pendiente'),(6,4,NULL,'pendiente',0.00,'2026-07-09 14:05:35','2026-07-09 14:05:35',0.00,0.00,'pendiente'),(7,4,NULL,'pagada',810.00,'2026-07-09 14:05:49','2026-07-09 14:08:12',0.00,0.00,'pendiente'),(8,4,NULL,'pendiente',800.00,'2026-07-09 14:07:17','2026-07-09 14:07:17',0.00,0.00,'pendiente'),(9,3,NULL,'pagada',800.00,'2026-07-09 14:14:38','2026-07-14 12:27:16',0.00,800.00,'pagada'),(10,3,NULL,'pagada',600.00,'2026-07-09 14:15:47','2026-07-20 10:53:22',0.00,600.00,'pagada'),(11,2,NULL,'pagada',700.00,'2026-07-09 14:17:05','2026-07-14 12:16:36',0.00,700.00,'pagada'),(12,NULL,'Miguel Perez','pagada',0.00,'2026-07-09 14:20:56','2026-07-09 14:21:12',0.00,0.00,'pendiente'),(13,1,NULL,'pagada',970.00,'2026-07-09 14:21:43','2026-07-09 14:21:44',0.00,0.00,'pendiente'),(14,NULL,'Cesar Gomez','pagada',830.00,'2026-07-09 14:22:42','2026-07-09 14:22:52',0.00,0.00,'pendiente'),(15,5,NULL,'pagada',1260.00,'2026-07-09 14:31:35','2026-07-09 14:31:58',0.00,0.00,'pendiente'),(16,3,NULL,'pagada',1600.00,'2026-07-14 12:39:53','2026-07-14 12:40:13',1500.00,100.00,'pagada'),(17,2,NULL,'pendiente',800.00,'2026-07-14 12:50:04','2026-07-14 12:52:32',0.00,800.00,'pagada'),(18,2,NULL,'pendiente',600.00,'2026-07-14 12:53:01','2026-07-14 12:53:01',600.00,0.00,'pagada'),(19,2,NULL,'pendiente',250.00,'2026-07-14 13:53:36','2026-07-14 13:53:36',250.00,0.00,'pagada'),(20,3,NULL,'pagada',250.00,'2026-07-14 14:31:39','2026-07-14 14:31:39',250.00,0.00,'pagada'),(21,3,NULL,'pendiente',800.00,'2026-07-14 14:32:08','2026-07-17 22:42:54',200.00,400.00,'parcial'),(22,NULL,'Miguel Perez','pagada',250.00,'2026-07-14 14:33:06','2026-07-14 14:33:17',0.00,250.00,'pagada'),(23,7,NULL,'pendiente',800.00,'2026-07-20 11:08:25','2026-07-20 11:08:25',0.00,0.00,'pendiente'),(24,3,NULL,'pagada',970.00,'2026-07-20 11:09:38','2026-07-20 13:53:36',0.00,970.00,'pagada'),(25,NULL,'Cesar Gomez','pagada',770.00,'2026-07-20 11:10:03','2026-07-20 13:38:24',0.00,770.00,'pagada'),(26,2,NULL,'pagada',780.00,'2026-07-20 11:10:23','2026-07-20 11:24:03',0.00,780.00,'pagada'),(27,8,NULL,'pagada',970.00,'2026-07-20 13:35:45','2026-07-20 13:36:35',0.00,970.00,'pagada'),(28,2,NULL,'pagada',250.00,'2026-07-20 13:43:09','2026-07-20 13:43:10',250.00,0.00,'pagada'),(29,8,NULL,'pagada',600.00,'2026-07-20 13:46:31','2026-07-20 13:47:29',0.00,600.00,'pagada'),(30,2,NULL,'pagada',850.00,'2026-07-20 13:57:09','2026-07-20 13:57:48',750.00,100.00,'pagada');
/*!40000 ALTER TABLE `ordenes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pacientes`
--

DROP TABLE IF EXISTS `pacientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pacientes` (
  `id_paciente` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(30) NOT NULL,
  `raza` varchar(20) NOT NULL,
  `edad` int NOT NULL,
  `especie` varchar(20) NOT NULL,
  `sexo` varchar(20) NOT NULL,
  `historia_clinica` varchar(800) NOT NULL,
  `inicio_problema` datetime DEFAULT NULL,
  `diagnostico_vet` varchar(500) NOT NULL,
  `id_cliente` int NOT NULL,
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_paciente`),
  KEY `id_cliente` (`id_cliente`),
  CONSTRAINT `pacientes_ibfk_1` FOREIGN KEY (`id_cliente`) REFERENCES `clientes` (`id_cliente`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pacientes`
--

LOCK TABLES `pacientes` WRITE;
/*!40000 ALTER TABLE `pacientes` DISABLE KEYS */;
INSERT INTO `pacientes` VALUES (1,'Brownie','Labrador Belga',1,'Canino','Hembra','Blah blah blah','2026-07-01 18:05:00','Necesita fisioterapia.',2,'2026-07-01 18:06:02','2026-07-01 18:06:02'),(2,'Chester','Tabby',11,'Felino','Macho','Problemas neurologicos','2026-06-28 18:10:00','Necesita Levivet',4,'2026-07-01 18:10:37','2026-07-01 18:10:37'),(3,'Chetos','Tabby',11,'Felino','Macho','Se le rompió un tendón.','2026-06-02 18:11:00','Necesita cirugía.',4,'2026-07-01 18:11:09','2026-07-01 18:11:09'),(4,'Mali','Snausser',11,'Canino','Hembra','llego por un problema','2026-04-30 14:00:00','fd gfd gfd gfdfg',5,'2026-07-09 14:00:52','2026-07-09 14:01:39'),(5,'Frances','Cuarto de milla',15,'Equino','Hembra','Infreccion en la muela','2026-07-06 14:29:00','-abse¡¡si',1,'2026-07-09 14:30:02','2026-07-09 14:30:02'),(6,'Pepper','Tabby',5,'Felino','Hembra','asdf asdf asdf','2026-07-06 11:41:00','asdf asdf asdf',6,'2026-07-14 11:42:02','2026-07-14 11:42:02'),(7,'Angie','Calico',4,'Felino','Hembra','asdfa sdf','2026-07-05 11:42:00','asdf asdf ',6,'2026-07-14 11:42:38','2026-07-14 11:42:38'),(8,'sisu','french poodle',4,'Canino','Hembra castrada','asd asd','2026-07-01 13:29:00','asd asd asd',7,'2026-07-20 13:29:37','2026-07-20 15:13:06'),(9,'Moka','Golden Retriever',10,'Canino','Macho castrado','',NULL,'',8,'2026-07-20 15:23:05','2026-07-20 15:23:05'),(10,'Tom','Tabby',6,'Felino','Macho castrado','asdf asdf','2026-07-07 15:39:00','',4,'2026-07-20 15:31:16','2026-07-20 15:39:43');
/*!40000 ALTER TABLE `pacientes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pagos_orden`
--

DROP TABLE IF EXISTS `pagos_orden`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pagos_orden` (
  `id_pago` int NOT NULL AUTO_INCREMENT,
  `id_orden` int NOT NULL,
  `monto` decimal(10,2) NOT NULL,
  `metodo_pago` enum('efectivo','transferencia') NOT NULL,
  `fecha_pago` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_pago`),
  KEY `id_orden` (`id_orden`),
  CONSTRAINT `pagos_orden_ibfk_1` FOREIGN KEY (`id_orden`) REFERENCES `ordenes` (`id_orden`) ON DELETE CASCADE,
  CONSTRAINT `pagos_orden_chk_1` CHECK ((`monto` > 0))
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pagos_orden`
--

LOCK TABLES `pagos_orden` WRITE;
/*!40000 ALTER TABLE `pagos_orden` DISABLE KEYS */;
INSERT INTO `pagos_orden` VALUES (1,11,400.00,'efectivo','2026-07-14 12:09:07','2026-07-14 12:09:07'),(2,11,300.00,'efectivo','2026-07-14 12:16:10','2026-07-14 12:16:10'),(3,10,200.00,'efectivo','2026-07-14 12:25:01','2026-07-14 12:25:01'),(4,9,800.00,'efectivo','2026-07-14 12:27:16','2026-07-14 12:27:16'),(5,16,100.00,'efectivo','2026-07-14 12:40:13','2026-07-14 12:40:13'),(6,17,400.00,'transferencia','2026-07-14 12:52:10','2026-07-14 12:52:10'),(7,17,400.00,'efectivo','2026-07-14 12:52:32','2026-07-14 12:52:32'),(8,22,250.00,'efectivo','2026-07-14 14:33:17','2026-07-14 14:33:17'),(9,21,400.00,'efectivo','2026-07-17 22:42:54','2026-07-17 22:42:54'),(10,10,400.00,'transferencia','2026-07-20 10:53:22','2026-07-20 10:53:22'),(11,26,80.00,'efectivo','2026-07-20 11:23:53','2026-07-20 11:23:53'),(12,26,700.00,'transferencia','2026-07-20 11:24:03','2026-07-20 11:24:03'),(13,27,970.00,'efectivo','2026-07-20 13:36:35','2026-07-20 13:36:35'),(14,25,500.00,'efectivo','2026-07-20 13:38:07','2026-07-20 13:38:07'),(15,25,270.00,'transferencia','2026-07-20 13:38:24','2026-07-20 13:38:24'),(16,24,370.00,'efectivo','2026-07-20 13:40:13','2026-07-20 13:40:13'),(17,29,600.00,'efectivo','2026-07-20 13:47:29','2026-07-20 13:47:29'),(18,24,600.00,'transferencia','2026-07-20 13:53:36','2026-07-20 13:53:36'),(19,30,100.00,'efectivo','2026-07-20 13:57:48','2026-07-20 13:57:48');
/*!40000 ALTER TABLE `pagos_orden` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `productos`
--

DROP TABLE IF EXISTS `productos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `productos` (
  `id_producto` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  `stock` int NOT NULL,
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_producto`),
  CONSTRAINT `productos_chk_1` CHECK ((`stock` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `productos`
--

LOCK TABLES `productos` WRITE;
/*!40000 ALTER TABLE `productos` DISABLE KEYS */;
INSERT INTO `productos` VALUES (1,'Crema para desinflamar',120.00,0,'2026-07-06 11:34:02','2026-07-20 09:51:43'),(2,'Llavero gatos',10.00,2,'2026-07-06 11:34:38','2026-07-20 11:10:23'),(3,'Premios Mutt',170.00,10,'2026-07-09 14:26:49','2026-07-20 13:35:45');
/*!40000 ALTER TABLE `productos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `servicios`
--

DROP TABLE IF EXISTS `servicios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `servicios` (
  `id_servicio` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(30) NOT NULL,
  `descripcion` varchar(200) NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_servicio`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `servicios`
--

LOCK TABLES `servicios` WRITE;
/*!40000 ALTER TABLE `servicios` DISABLE KEYS */;
INSERT INTO `servicios` VALUES (1,'Fisioterapia','Sesión de fisioterapia primera consulta.',800.00,'2026-07-06 11:45:23','2026-07-09 14:17:22'),(2,'Laser','Sesión de laser para ayudar a los huesos y músculos.',250.00,'2026-07-06 11:45:54','2026-07-06 11:45:54'),(3,'Fisioterapia','Sesión de fisioterapia',600.00,'2026-07-09 14:14:10','2026-07-09 14:14:10');
/*!40000 ALTER TABLE `servicios` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-07-20 16:04:51
