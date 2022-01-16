CREATE DATABASE medilearn_db default CHARACTER SET UTF8;

use medilearn_db;

CREATE TABLE medilearn_table(
    medi_id INT(10) NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    saved VARCHAR(100) NOT NULL,
    created DATETIME NOT NULL,
    spo2 json,
    hr json,
    ppg json,
    PRIMARY KEY(medi_id)
);

CREATE TABLE ai_table(
    ai_id INT(10) NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    saved VARCHAR(100) NOT NULL,
    created DATETIME NOT NULL,
    ppg json,
    spoint json,
    opoint json,
    wpoint json,
    rs json,
    ai_hr json,
    ai_hrv json,
    ai_segment json,
    PRIMARY KEY(ai_id)
);

-- source C:\Users\KJW\PycharmProjects\My_project\mediLearn_api\schema\medilearn_db.sql
-- 위 코드와 같이 source + sql 파일경로를 cmd에 입력하여 sql 코드를 실행할 수 잇음
-- source = 외부 SQL script file을 읽어와서 실행하기 위한 명령어
