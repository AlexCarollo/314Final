DROP TABLE `BMart`;
DROP TABLE `BMart Address`;
DROP TABLE `Brand`;
DROP TABLE `Customer`;
DROP TABLE `Customer Address`;
DROP TABLE `Customer Cart`;
DROP TABLE `Hours of Operation`;
DROP TABLE `Inventory`;
DROP TABLE `Product`;
DROP TABLE `Product Type`;
DROP TABLE `Reorder Requests`;
DROP TABLE `Requested Product`;
DROP TABLE `Shipments`;
DROP TABLE `Shipped Product`;
DROP TABLE `Vendor`;
DROP TABLE `Vendor Address`;


CREATE TABLE `BMart` (
  `store_id` int NOT NULL AUTO_INCREMENT,
  `phone_number` char(10) NOT NULL,
  PRIMARY KEY (`store_id`)
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `BMart Address` (
  `store_id` int NOT NULL,
  `addr_line_one` varchar(64) NOT NULL,
  `addr_line_two` varchar(64) DEFAULT NULL,
  `city` varchar(64) NOT NULL,
  `state` char(2) NOT NULL,
  `country` varchar(64) NOT NULL,
  `zip` char(5) NOT NULL,
  PRIMARY KEY (`store_id`),
  CONSTRAINT `bmart_address_id` FOREIGN KEY (`store_id`) REFERENCES `BMart` (`store_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `Brand` (
  `brand_name` varchar(50) NOT NULL,
  `vend_id` int DEFAULT NULL,
  PRIMARY KEY (`brand_name`),
  KEY `brand_vendor_id` (`vend_id`),
  CONSTRAINT `brand_vendor_id` FOREIGN KEY (`vend_id`) REFERENCES `Vendor` (`vend_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `Customer` (
  `cust_id` int NOT NULL AUTO_INCREMENT,
  `cust_name` varchar(64) NOT NULL,
  `cust_email` varchar(64) DEFAULT NULL,
  `cust_phone` char(10) DEFAULT NULL,
  PRIMARY KEY (`cust_id`)
) ENGINE=InnoDB AUTO_INCREMENT=96 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `Customer Address` (
  `cust_id` int NOT NULL,
  `addr_line_one` varchar(64) NOT NULL,
  `addr_line_two` varchar(64) DEFAULT NULL,
  `city` varchar(64) NOT NULL,
  `state` char(2) NOT NULL,
  `country` varchar(64) NOT NULL,
  `zip` char(5) NOT NULL,
  PRIMARY KEY (`cust_id`,`zip`),
  CONSTRAINT `customer_address_id` FOREIGN KEY (`cust_id`) REFERENCES `Customer` (`cust_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `Customer Cart` (
  `cart_id` int NOT NULL AUTO_INCREMENT,
  `cust_id` int NOT NULL,
  `UPC` char(12) NOT NULL,
  `store_id` int NOT NULL,
  `prod_quantity` int NOT NULL,
  `total_price` int NOT NULL,
  `successfully_ordered` tinyint NOT NULL DEFAULT '0',
  PRIMARY KEY (`cart_id`),
  KEY `cart_UPC_idx` (`UPC`),
  KEY `cart_store_idx` (`store_id`),
  CONSTRAINT `cart_store` FOREIGN KEY (`store_id`) REFERENCES `BMart` (`store_id`) ON DELETE CASCADE,
  CONSTRAINT `cart_UPC` FOREIGN KEY (`UPC`) REFERENCES `Product` (`UPC`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `Hours of Operation` (
  `store_id` int NOT NULL,
  `weekday_op` time NOT NULL,
  `weekday_cl` time NOT NULL,
  `weekend_op` time NOT NULL,
  `weekend_cl` time NOT NULL,
  PRIMARY KEY (`store_id`),
  CONSTRAINT `hours_store_id` FOREIGN KEY (`store_id`) REFERENCES `BMart` (`store_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `Inventory` (
  `store_id` int NOT NULL,
  `UPC` char(12) NOT NULL,
  `sales_price` int DEFAULT NULL,
  `inv_space` int NOT NULL,
  `max_inv_space` int NOT NULL,
  PRIMARY KEY (`store_id`,`UPC`),
  KEY `UPC_idx` (`UPC`),
  CONSTRAINT `inventory_store_id` FOREIGN KEY (`store_id`) REFERENCES `BMart` (`store_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `inventory_UPC` FOREIGN KEY (`UPC`) REFERENCES `Product` (`UPC`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `Product` (
  `UPC` char(12) NOT NULL,
  `product_name` varchar(45) NOT NULL,
  `product_size` int NOT NULL,
  `unit_price` int NOT NULL,
  `standard_price` int NOT NULL,
  `source_nation` varchar(50) NOT NULL,
  `brand` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`UPC`),
  KEY `product_brand_idx` (`brand`),
  CONSTRAINT `product_brand` FOREIGN KEY (`brand`) REFERENCES `Brand` (`brand_name`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `Product Type` (
  `UPC` char(12) NOT NULL,
  `product_type` varchar(45) NOT NULL,
  PRIMARY KEY (`UPC`,`product_type`),
  CONSTRAINT `product_type_UPC` FOREIGN KEY (`UPC`) REFERENCES `Product` (`UPC`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `Reorder Requests` (
  `request_id` int NOT NULL AUTO_INCREMENT,
  `order_status` varchar(10) NOT NULL,
  `order_seen` tinyint NOT NULL,
  `reoder_date` date NOT NULL,
  `reorder_received_date` date DEFAULT NULL,
  `store_id` int NOT NULL,
  `vendor_id` int NOT NULL,
  PRIMARY KEY (`request_id`),
  KEY `reorder_store_id_idx` (`store_id`),
  KEY `reorder_vendor_id_idx` (`vendor_id`),
  CONSTRAINT `reorder_store_id` FOREIGN KEY (`store_id`) REFERENCES `BMart` (`store_id`),
  CONSTRAINT `reorder_vendor_id` FOREIGN KEY (`vendor_id`) REFERENCES `Vendor` (`vend_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `Requested Product` (
  `UPC` char(12) NOT NULL,
  `request_id` int NOT NULL,
  `quantity` int DEFAULT NULL,
  PRIMARY KEY (`UPC`,`request_id`),
  KEY `requested_product_reorder_id_idx` (`request_id`),
  CONSTRAINT `requested_product_reorder_id` FOREIGN KEY (`request_id`) REFERENCES `Reorder Requests` (`request_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `requested_product_UPC` FOREIGN KEY (`UPC`) REFERENCES `Product` (`UPC`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `Shipments` (
  `ship_id` int NOT NULL AUTO_INCREMENT,
  `total_price` int NOT NULL,
  `date_sent` date NOT NULL,
  `store_id` int NOT NULL,
  `request_id` int NOT NULL,
  `vend_id` int NOT NULL,
  PRIMARY KEY (`ship_id`),
  KEY `shipment_store_id_idx` (`store_id`),
  KEY `shipment_request_id_idx` (`request_id`),
  KEY `shipment_vendor_id_idx` (`vend_id`),
  CONSTRAINT `shipment_request_id` FOREIGN KEY (`request_id`) REFERENCES `Reorder Requests` (`request_id`),
  CONSTRAINT `shipment_store_id` FOREIGN KEY (`store_id`) REFERENCES `BMart` (`store_id`),
  CONSTRAINT `shipment_vendor_id` FOREIGN KEY (`vend_id`) REFERENCES `Vendor` (`vend_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `Shpped Product` (
  `UPC` char(12) NOT NULL,
  `ship_id` int NOT NULL,
  `quantity` int NOT NULL,
  PRIMARY KEY (`UPC`,`ship_id`),
  KEY `shipped_product_shipment_id_idx` (`ship_id`),
  CONSTRAINT `shipped_product_shipment_id` FOREIGN KEY (`ship_id`) REFERENCES `Shipments` (`ship_id`),
  CONSTRAINT `shipped_product_UPC` FOREIGN KEY (`UPC`) REFERENCES `Product` (`UPC`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `Vendor` (
  `vend_id` int NOT NULL AUTO_INCREMENT,
  `vend_name` varchar(50) NOT NULL,
  `email` varchar(64) NOT NULL,
  `phone_number` char(10) NOT NULL,
  PRIMARY KEY (`vend_id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `Vendor Address` (
  `vend_id` int NOT NULL,
  `addr_line_one` varchar(64) NOT NULL,
  `addr_line_two` varchar(64) DEFAULT NULL,
  `city` varchar(64) NOT NULL,
  `state` char(2) NOT NULL,
  `country` varchar(64) NOT NULL,
  `zip` char(5) NOT NULL,
  PRIMARY KEY (`vend_id`),
  CONSTRAINT `vendor_address_id` FOREIGN KEY (`vend_id`) REFERENCES `Vendor` (`vend_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
