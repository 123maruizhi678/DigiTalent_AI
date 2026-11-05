-- 仅供授权的独立 MySQL 测试空库人工准备；不得应用到业务库。
CREATE TABLE test_common_example (
 id CHAR(32) NOT NULL PRIMARY KEY,
 name VARCHAR(30) NOT NULL,
 created_at DATETIME(6) NOT NULL,
 updated_at DATETIME(6) NOT NULL,
 status VARCHAR(8) NOT NULL DEFAULT 'active',
 CONSTRAINT ck_test_common_example_record_status CHECK (status IN ('active','inactive'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_bin;
CREATE TABLE test_common_child (
 id CHAR(32) NOT NULL PRIMARY KEY,
 parent_id CHAR(32) NOT NULL,
 FOREIGN KEY (parent_id) REFERENCES test_common_example(id) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_bin;
CREATE TABLE test_time_only (
 `key` INTEGER NOT NULL PRIMARY KEY,
 created_at DATETIME(6) NOT NULL,
 updated_at DATETIME(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_bin;
CREATE TABLE test_status_only (
 `key` INTEGER NOT NULL PRIMARY KEY,
 status VARCHAR(8) NOT NULL DEFAULT 'active',
 CONSTRAINT ck_test_status_only_record_status CHECK (status IN ('active','inactive'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_bin;
