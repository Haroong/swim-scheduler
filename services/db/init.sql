-- 수영장 스케줄 데이터베이스 초기화 스크립트
-- MariaDB 컨테이너 시작 시 자동 실행됨

-- 테이블이 없으면 생성 (IF NOT EXISTS)

-- 1. facility (시설)
CREATE TABLE IF NOT EXISTS facility (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. notice (공지사항)
CREATE TABLE IF NOT EXISTS notice (
    id INT AUTO_INCREMENT PRIMARY KEY,
    facility_id INT NOT NULL,
    title VARCHAR(500) NOT NULL,
    source_url VARCHAR(500) NOT NULL UNIQUE,
    valid_date VARCHAR(7),
    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (facility_id) REFERENCES facility(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. swim_schedule (스케줄)
CREATE TABLE IF NOT EXISTS swim_schedule (
    id INT AUTO_INCREMENT PRIMARY KEY,
    facility_id INT NOT NULL,
    day_type ENUM('평일', '토요일', '일요일') NOT NULL,
    season ENUM('하절기', '동절기'),
    valid_month VARCHAR(7) NOT NULL,
    FOREIGN KEY (facility_id) REFERENCES facility(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. swim_session (세션)
CREATE TABLE IF NOT EXISTS swim_session (
    id INT AUTO_INCREMENT PRIMARY KEY,
    schedule_id INT NOT NULL,
    session_name VARCHAR(50) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    capacity INT,
    lanes INT,
    applicable_days VARCHAR(20),  -- 적용 요일 (NULL=전체, "수"=수요일만, "월,수,금"=월수금)
    FOREIGN KEY (schedule_id) REFERENCES swim_schedule(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. fee (이용료)
CREATE TABLE IF NOT EXISTS fee (
    id INT AUTO_INCREMENT PRIMARY KEY,
    facility_id INT NOT NULL,
    category VARCHAR(100) NOT NULL,
    price INT NOT NULL,
    note TEXT,
    FOREIGN KEY (facility_id) REFERENCES facility(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_schedule_facility ON swim_schedule(facility_id);
CREATE INDEX IF NOT EXISTS idx_schedule_valid_month ON swim_schedule(valid_month);
CREATE INDEX IF NOT EXISTS idx_session_schedule ON swim_session(schedule_id);
CREATE INDEX IF NOT EXISTS idx_notice_facility ON notice(facility_id);
CREATE INDEX IF NOT EXISTS idx_fee_facility ON fee(facility_id);
