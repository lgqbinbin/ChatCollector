# env
## mysql
```sh
pip install pymysql

mysql -u root -p 114514

SHOW DATABASES;


DROP DATABASE chatcollector_db;
CREATE DATABASE chatcollector_db;


```

## django
```sh
pip install django
```
# quickStart

```sh
django-admin startproject ChatCollector

cd ChatCollector
python manage.py startapp myapp # 创建一个新的应用

python manage.py runserver


```
# 数据库功能
```sh
python manage.py makemigrations # 检查模型并生成相应的迁移文件。
python manage.py migrate # 根据生成的迁移文件在数据库中创建或修改相应的表。

python manage.py migrate main # 只应用你自己的迁移
```