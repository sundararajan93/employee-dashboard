# EMPLOYEE DASHBOARD (BETA)

1. Creating Flask container

```
docker build -t ourstaff_image .
```

2. Running Flask container

```
docker run --name ourstaff_container -p 5001:5000 -d ourstaff_image
```

3. Creating Mysql Image

```
docker build -f Dockerfile.mysql -t mysql_image .
```

4. Creating MySql Container

```
docker container run --name mysql_container -d -p 3308:3306 mysql_image
```

5. Creating Table to mysql container

```
docker exec -it mysql_container bash

mysql -u root -ppassword
create database ourstaffapp;
use ourstaffapp;
CREATE TABLE users (id INT(15) PRIMARY KEY AUTO_INCREMENT,
                    name VARCHAR(100), email VARCHAR(100),
                    username VARCHAR(100), password VARCHAR(100),
                    register_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP());

```