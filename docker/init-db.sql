-- PostGIS 확장 활성화
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- 관리자 계정
CREATE TABLE IF NOT EXISTS users (
    id          BIGSERIAL PRIMARY KEY,
    username    VARCHAR(50)  UNIQUE NOT NULL,
    password    VARCHAR(255) NOT NULL,
    role        VARCHAR(20)  NOT NULL DEFAULT 'ADMIN',
    created_at  TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- 도로 파손 탐지 결과
CREATE TABLE IF NOT EXISTS road_damage (
    id            BIGSERIAL PRIMARY KEY,
    damage_type   VARCHAR(20)  NOT NULL,
    confidence    FLOAT        NOT NULL,
    location      GEOMETRY(Point, 4326) NOT NULL,
    image_path    VARCHAR(500),
    bbox_x        FLOAT,
    bbox_y        FLOAT,
    bbox_w        FLOAT,
    bbox_h        FLOAT,
    road_name     VARCHAR(200),
    district      VARCHAR(100),
    detected_at   TIMESTAMP    NOT NULL DEFAULT NOW(),
    created_at    TIMESTAMP    NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_road_damage_location ON road_damage USING GIST(location);
CREATE INDEX IF NOT EXISTS idx_road_damage_type     ON road_damage(damage_type);
CREATE INDEX IF NOT EXISTS idx_road_damage_detected ON road_damage(detected_at);

-- 기상 관측소
CREATE TABLE IF NOT EXISTS weather_station (
    id            BIGSERIAL PRIMARY KEY,
    station_id    VARCHAR(20)  UNIQUE NOT NULL,
    station_name  VARCHAR(100) NOT NULL,
    station_type  VARCHAR(10)  NOT NULL,
    location      GEOMETRY(Point, 4326) NOT NULL,
    region        VARCHAR(100),
    created_at    TIMESTAMP    NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_weather_station_location ON weather_station USING GIST(location);

-- 블랙아이스 위험도 예측
CREATE TABLE IF NOT EXISTS blackice_risk (
    id              BIGSERIAL PRIMARY KEY,
    station_id      VARCHAR(20)  NOT NULL REFERENCES weather_station(station_id),
    location        GEOMETRY(Point, 4326) NOT NULL,
    risk_level      SMALLINT     NOT NULL CHECK (risk_level BETWEEN 0 AND 3),
    risk_label      VARCHAR(10)  NOT NULL,
    temperature     FLOAT,
    humidity        FLOAT,
    precipitation   FLOAT,
    wind_speed      FLOAT,
    road_temp       FLOAT,
    predicted_at    TIMESTAMP    NOT NULL,
    created_at      TIMESTAMP    NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_blackice_location   ON blackice_risk USING GIST(location);
CREATE INDEX IF NOT EXISTS idx_blackice_risk_level ON blackice_risk(risk_level);
CREATE INDEX IF NOT EXISTS idx_blackice_predicted  ON blackice_risk(predicted_at);

-- AI 배치 처리 이력
CREATE TABLE IF NOT EXISTS detection_batch (
    id            BIGSERIAL PRIMARY KEY,
    batch_type    VARCHAR(20)  NOT NULL,
    status        VARCHAR(20)  NOT NULL DEFAULT 'PENDING',
    total_files   INT          DEFAULT 0,
    processed     INT          DEFAULT 0,
    error_msg     TEXT,
    started_at    TIMESTAMP,
    finished_at   TIMESTAMP,
    created_at    TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- 기본 관리자 계정 (password: admin1234, bcrypt)
-- password: admin1234
INSERT INTO users (username, password, role)
VALUES ('admin', '$2b$10$wKKaw5ihUBYxip.i78c.veo1gIJC0LJFHutCYvrWz4FUkGAmPa3na', 'ADMIN')
ON CONFLICT (username) DO NOTHING;

-- 기상 관측소 샘플 데이터
INSERT INTO weather_station (station_id, station_name, station_type, location, region) VALUES
('108', '서울', 'ASOS', ST_SetSRID(ST_MakePoint(126.9658, 37.5714), 4326), '서울특별시'),
('119', '수원', 'ASOS', ST_SetSRID(ST_MakePoint(126.9831, 37.2636), 4326), '경기도'),
('133', '대전', 'ASOS', ST_SetSRID(ST_MakePoint(127.3718, 36.3714), 4326), '대전광역시'),
('143', '대구', 'ASOS', ST_SetSRID(ST_MakePoint(128.6189, 35.8831), 4326), '대구광역시'),
('156', '광주', 'ASOS', ST_SetSRID(ST_MakePoint(126.8914, 35.1722), 4326), '광주광역시'),
('159', '부산', 'ASOS', ST_SetSRID(ST_MakePoint(129.0317, 35.1044), 4326), '부산광역시')
ON CONFLICT (station_id) DO NOTHING;
