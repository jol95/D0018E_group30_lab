-- MySQL Script generated by MySQL Workbench
-- Wed 27 Nov 2019 09:29:38 PM CET
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema webshop
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `webshop` DEFAULT CHARACTER SET utf8 ;
USE `webshop` ;


-- -----------------------------------------------------
-- Table `webshop`.`products`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `webshop`.`products` (
  `prodID` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(60) NOT NULL,
  `desc` MEDIUMTEXT NULL,
  `price` INT NOT NULL,
  `img` VARCHAR(45) NULL,
  `stock` INT NOT NULL,
  `category` INT NULL,
  `discount` DECIMAL(4) NULL,
  PRIMARY KEY (`prodID`))
ENGINE = InnoDB
AUTO_INCREMENT = 10000


-- -----------------------------------------------------
-- Table `webshop`.`customers`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `webshop`.`customers` (
  `custID` INT NOT NULL AUTO_INCREMENT,
  `firstname` VARCHAR(25) NOT NULL,
  `lastname` VARCHAR(25) NOT NULL,
  `email` VARCHAR(320) NOT NULL,
  `password` VARCHAR(320) NOT NULL,
  `address` VARCHAR(95) NOT NULL,
  `postcode` VARCHAR(5) NOT NULL,
  `country` VARCHAR(45) NOT NULL,
  `phoneno` VARCHAR(15) NULL,
  PRIMARY KEY (`custID`),
  UNIQUE INDEX `email_UNIQUE` (`email` ASC))
ENGINE = InnoDB
AUTO_INCREMENT = 800000


-- -----------------------------------------------------
-- Table `webshop`.`cart`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `webshop`.`cart` (
  `cartID` INT NOT NULL AUTO_INCREMENT,
  `prodID` INT NOT NULL,
  `custID` INT NOT NULL,
  `qty` INT NOT NULL,
  PRIMARY KEY (`cartID`),
  INDEX `prodID_idx` (`prodID` ASC),
  CONSTRAINT `prodID`
    FOREIGN KEY (`prodID`)
    REFERENCES `webshop`.`products` (`prodID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `custID`
    FOREIGN KEY (`custID`)
    REFERENCES `webshop`.`customers` (`custID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 70000;


-- -----------------------------------------------------
-- Table `webshop`.`employees`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `webshop`.`employees` (
  `employeeID` INT NOT NULL AUTO_INCREMENT,
  `firstname` VARCHAR(25) NOT NULL,
  `lastname` VARCHAR(25) NOT NULL,
  `username` VARCHAR(45) NOT NULL,
  `password` VARCHAR(45) NOT NULL,
  `role` VARCHAR(45) NULL,
  PRIMARY KEY (`employeeID`),
  UNIQUE INDEX `username_UNIQUE` (`username` ASC))
ENGINE = InnoDB
AUTO_INCREMENT = 9000;


-- -----------------------------------------------------
-- Table `webshop`.`orders`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `webshop`.`orders` (
  `orderID` INT NOT NULL AUTO_INCREMENT,
  `custID` INT NOT NULL,
  PRIMARY KEY (`orderID`),
  INDEX `fk_custID_idx` (`custID` ASC),
  CONSTRAINT `fk_custID`
    FOREIGN KEY (`custID`)
    REFERENCES `webshop`.`customers` (`custID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `webshop`.`orderlines`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `webshop`.`orderlines` (
  `ordln` INT NOT NULL AUTO_INCREMENT,
  `orderID` INT NOT NULL,
  `prodID` INT NOT NULL,
  `qty` INT NOT NULL,
  PRIMARY KEY (`ordln`),
  UNIQUE INDEX `orderlinescol_UNIQUE` (`orderID` ASC),
  INDEX `fk_prodID_idx` (`prodID` ASC),
  CONSTRAINT `fk_orderID`
    FOREIGN KEY (`orderID`)
    REFERENCES `webshop`.`orders` (`orderID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_prodID`
    FOREIGN KEY (`prodID`)
    REFERENCES `webshop`.`products` (`prodID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `webshop`.`reviews`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `webshop`.`reviews` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `prodID` INT(11) NOT NULL,
  `custID` INT(11) NOT NULL,
  `text` TINYTEXT NOT NULL,
  `date` VARCHAR(45) NOT NULL,
  `rating` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `prodID_idx` (`prodID` ASC),
  INDEX `fk_custID_idx` (`custID` ASC),
  CONSTRAINT `fk_custID`
    FOREIGN KEY (`custID`)
    REFERENCES `webshop`.`customers` (`custID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_prodID`
    FOREIGN KEY (`prodID`)
    REFERENCES `webshop`.`products` (`prodID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB

-- -----------------------------------------------------
-- Populate product table
-- -----------------------------------------------------
INSERT INTO `products` (`name`, `desc`, `price`, `img`, `stock`) VALUES
    ('Brun stickad mössa', '', 100, 'brun-stickad-mössa.jpg', 20),
    ('Blå stickad mössa', '', 100, '', 20),
    ('Grön stickad mössa', '', 100, '', 20),
    ('Gul stickad mössa', '', 100, '', 20),
    ('Svart stickad mössa', '', 100, '', 20),
    ('Lila stickad mössa', '', 100, '', 20),
    ('Transparant stickad mössa', '', 100, '', 20);


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;