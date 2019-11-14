# D0018E_group30_lab


## Anslut till AWS ##
1. cd till mappen där din personliga nyckel finns.

2. skriv in kommandot (ex. d0018e-gr30.pem är filnamnet på nyckel)

    chmod 400 "nyckelns filnamn"

3. Anslut till servern via SSH med nyckeln
    
    ssh -i "nyckelns filnamn" ubuntu@ec2-13-53-70-153.eu-north-1.compute.amazonaws.com

## MYSQL databas ##
host = localhost

user = root

password = Choss!95

database = webshop

## CREATE PRODUCT TABLE ##

CREATE TABLE IF NOT EXISTS `webshop`.`products` (
  `prodID` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(60) NOT NULL,
  `desc` MEDIUMTEXT NULL,
  `price` INT NOT NULL,
  `img` VARCHAR(45) NULL,
  PRIMARY KEY (`prodID`))
ENGINE = InnoDB