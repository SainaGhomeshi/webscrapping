import mysql.connector


# create database
db = mysql.connector.connect(user='root',
                             password='',
                             host='localhost')
cursor = db.cursor()
create_db_command = 'CREATE DATABASE `web_scraping`;'
cursor.execute(create_db_command)
# grant access
create_user_command = '''
    CREATE USER 'web_scraping_user'@'localhost' IDENTIFIED BY '!@#123qwe';
    GRANT ALL PRIVILEGES ON *.* TO 'web_scraping_user'@'localhost' REQUIRE NONE WITH GRANT OPTION MAX_QUERIES_PER_HOUR 0 MAX_CONNECTIONS_PER_HOUR 0 MAX_UPDATES_PER_HOUR 0 MAX_USER_CONNECTIONS 0;
'''
cursor.execute(create_user_command)
# create table
db = mysql.connector.connect(user='root',
                             password='',
                             host='localhost',
                             database='web_scraping')
cursor = db.cursor()
create_table_command = '''
    CREATE TABLE `notices`(
    id INT AUTO_INCREMENT PRIMARY KEY,
    notice_title TEXT NULL,
    published_date DATE NULL,
    company_name TEXT NULL,
    company_ACN TEXT NULL,
    company_status TEXT NULL,
    notice_link TEXT NULL)
'''
cursor.execute(create_table_command)
print('database and table created successfully')
