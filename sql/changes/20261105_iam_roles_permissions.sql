-- P6-IAM-002 人工维护增量 SQL；仅供评审，未经授权禁止执行。
-- 前置：P6-IAM-001 已实施。不得重复执行；UUID/UTC时间由调用方提供。
-- inactive 不释放唯一名额；is_deleted=1 释放，历史禁止恢复。

CREATE TABLE sys_role (
    role_code VARCHAR(64) NOT NULL,
    role_name VARCHAR(200) NOT NULL,
    description VARCHAR(1000) NULL,
    id CHAR(32) NOT NULL,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    status VARCHAR(8) NOT NULL DEFAULT 'active',
    is_deleted BOOL NOT NULL DEFAULT 0,
    active_key TINYINT GENERATED ALWAYS AS (CASE WHEN is_deleted=0 THEN 1 ELSE NULL END) VIRTUAL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_sys_role_code_active (role_code, active_key),
    KEY ix_sys_role_deleted_status (is_deleted, status),
    CONSTRAINT ck_sys_role_text CHECK (CHAR_LENGTH(TRIM(role_code)) > 0 AND CHAR_LENGTH(TRIM(role_name)) > 0),
    CONSTRAINT ck_sys_role_deleted CHECK (is_deleted IN (0,1)),
    CONSTRAINT ck_sys_role_record_status CHECK (status IN ('active', 'inactive'))
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_bin;

CREATE TABLE sys_permission (
    permission_code VARCHAR(128) NOT NULL,
    permission_name VARCHAR(200) NOT NULL,
    resource_type VARCHAR(128) NOT NULL,
    action VARCHAR(64) NOT NULL,
    id CHAR(32) NOT NULL,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    status VARCHAR(8) NOT NULL DEFAULT 'active',
    is_deleted BOOL NOT NULL DEFAULT 0,
    active_key TINYINT GENERATED ALWAYS AS (CASE WHEN is_deleted=0 THEN 1 ELSE NULL END) VIRTUAL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_sys_permission_code_active (permission_code, active_key),
    KEY ix_sys_permission_resource_action (resource_type, action, is_deleted, status),
    CONSTRAINT ck_sys_permission_text CHECK (CHAR_LENGTH(TRIM(permission_code)) > 0 AND CHAR_LENGTH(TRIM(permission_name)) > 0 AND CHAR_LENGTH(TRIM(resource_type)) > 0 AND CHAR_LENGTH(TRIM(action)) > 0),
    CONSTRAINT ck_sys_permission_deleted CHECK (is_deleted IN (0,1)),
    CONSTRAINT ck_sys_permission_record_status CHECK (status IN ('active', 'inactive'))
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_bin;

CREATE TABLE sys_user_role (
    user_id CHAR(32) NOT NULL,
    role_id CHAR(32) NOT NULL,
    id CHAR(32) NOT NULL,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    status VARCHAR(8) NOT NULL DEFAULT 'active',
    is_deleted BOOL NOT NULL DEFAULT 0,
    active_key TINYINT GENERATED ALWAYS AS (CASE WHEN is_deleted=0 THEN 1 ELSE NULL END) VIRTUAL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_sys_user_role_active (user_id, role_id, active_key),
    KEY ix_sys_user_role_role (role_id, is_deleted, status, user_id),
    CONSTRAINT fk_sys_user_role_user_id_sys_user FOREIGN KEY (user_id) REFERENCES sys_user(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_sys_user_role_role_id_sys_role FOREIGN KEY (role_id) REFERENCES sys_role(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT ck_sys_user_role_deleted CHECK (is_deleted IN (0,1)),
    CONSTRAINT ck_sys_user_role_record_status CHECK (status IN ('active', 'inactive'))
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_bin;

CREATE TABLE sys_role_permission (
    role_id CHAR(32) NOT NULL,
    permission_id CHAR(32) NOT NULL,
    id CHAR(32) NOT NULL,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    status VARCHAR(8) NOT NULL DEFAULT 'active',
    is_deleted BOOL NOT NULL DEFAULT 0,
    active_key TINYINT GENERATED ALWAYS AS (CASE WHEN is_deleted=0 THEN 1 ELSE NULL END) VIRTUAL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_sys_role_permission_active (role_id, permission_id, active_key),
    KEY ix_sys_role_permission_permission (permission_id, is_deleted, status, role_id),
    CONSTRAINT fk_sys_role_permission_role_id_sys_role FOREIGN KEY (role_id) REFERENCES sys_role(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_sys_role_permission_permission_id_sys_permission FOREIGN KEY (permission_id) REFERENCES sys_permission(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT ck_sys_role_permission_deleted CHECK (is_deleted IN (0,1)),
    CONSTRAINT ck_sys_role_permission_record_status CHECK (status IN ('active', 'inactive'))
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_bin;

CREATE TABLE sys_data_scope (
    subject_type VARCHAR(16) NOT NULL,
    subject_id CHAR(32) NOT NULL,
    scope_type VARCHAR(16) NOT NULL,
    scope_value VARCHAR(128) NOT NULL DEFAULT '',
    starts_at DATETIME(6) NULL,
    expires_at DATETIME(6) NULL,
    id CHAR(32) NOT NULL,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    status VARCHAR(8) NOT NULL DEFAULT 'active',
    is_deleted BOOL NOT NULL DEFAULT 0,
    active_key TINYINT GENERATED ALWAYS AS (CASE WHEN is_deleted=0 THEN 1 ELSE NULL END) VIRTUAL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_sys_data_scope_active (subject_type, subject_id, scope_type, scope_value, active_key),
    KEY ix_sys_data_scope_subject (subject_type, subject_id, is_deleted, status),
    CONSTRAINT ck_sys_data_scope_subject CHECK (subject_type IN ('user','role')),
    CONSTRAINT ck_sys_data_scope_scope CHECK (scope_type IN ('all','dept','self','project')),
    CONSTRAINT ck_sys_data_scope_value CHECK ((scope_type IN ('all','self') AND scope_value = '') OR (scope_type IN ('dept','project') AND CHAR_LENGTH(TRIM(scope_value)) > 0)),
    CONSTRAINT ck_sys_data_scope_period CHECK (expires_at IS NULL OR (starts_at IS NOT NULL AND expires_at > starts_at)),
    CONSTRAINT ck_sys_data_scope_deleted CHECK (is_deleted IN (0,1)),
    CONSTRAINT ck_sys_data_scope_record_status CHECK (status IN ('active', 'inactive'))
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_bin;

DELIMITER $$
CREATE TRIGGER trg_sys_role_before_update
BEFORE UPDATE ON sys_role FOR EACH ROW
BEGIN
    IF OLD.is_deleted=1 AND NEW.is_deleted=0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Deleted authorization cannot be restored';
    END IF;
    IF NOT (OLD.id <=> NEW.id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Authorization id is immutable';
    END IF;
END$$
CREATE TRIGGER trg_sys_permission_before_update
BEFORE UPDATE ON sys_permission FOR EACH ROW
BEGIN
    IF OLD.is_deleted=1 AND NEW.is_deleted=0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Deleted authorization cannot be restored';
    END IF;
    IF NOT (OLD.id <=> NEW.id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Authorization id is immutable';
    END IF;
END$$
CREATE TRIGGER trg_sys_user_role_before_update
BEFORE UPDATE ON sys_user_role FOR EACH ROW
BEGIN
    IF OLD.is_deleted=1 AND NEW.is_deleted=0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Deleted authorization cannot be restored';
    END IF;
    IF NOT (OLD.id <=> NEW.id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Authorization id is immutable';
    END IF;
END$$
CREATE TRIGGER trg_sys_role_permission_before_update
BEFORE UPDATE ON sys_role_permission FOR EACH ROW
BEGIN
    IF OLD.is_deleted=1 AND NEW.is_deleted=0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Deleted authorization cannot be restored';
    END IF;
    IF NOT (OLD.id <=> NEW.id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Authorization id is immutable';
    END IF;
END$$
CREATE TRIGGER trg_sys_data_scope_before_update
BEFORE UPDATE ON sys_data_scope FOR EACH ROW
BEGIN
    IF OLD.is_deleted=1 AND NEW.is_deleted=0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Deleted authorization cannot be restored';
    END IF;
    IF NOT (OLD.id <=> NEW.id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Authorization id is immutable';
    END IF;
END$$
DELIMITER ;

