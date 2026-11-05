"""人工 SQL 与 ORM 的静态一致性检查，不执行数据库语句。"""

import re
from pathlib import Path

from sqlalchemy import CheckConstraint
from sqlalchemy.dialects import mysql

from app.core.orm import Base
from app.models import register_models

SQL = (Path(__file__).resolve().parents[2] / "sql/init.sql").read_text(encoding="utf-8")


def normalize(value):
    return re.sub(r"\s+", "", str(value)).lower()


def test_manual_sql_matches_model_columns_and_constraints():
    register_models()
    for name in ("sys_organization", "sys_user", "sys_user_organization"):
        table = Base.metadata.tables[name]
        body = SQL.split(f"CREATE TABLE {name} (", 1)[1].split(") ENGINE=InnoDB", 1)[0]
        declarations = {}
        for line in body.splitlines():
            match = re.match(r"    ([a-z_]+) (.+?)(?:,)?$", line)
            if match:
                declarations[match[1]] = match[2].rstrip(",")
        assert set(declarations) == set(table.c.keys())
        for column in table.c:
            declaration = declarations[column.name]
            expected_type = column.type.compile(dialect=mysql.dialect())
            assert normalize(declaration).startswith(normalize(expected_type))
            if column.computed is not None:
                assert normalize(column.computed.sqltext) in normalize(declaration)
                assert "VIRTUAL" in declaration
            else:
                assert ("NOT NULL" in declaration) == (not column.nullable)
                if column.server_default is not None:
                    default = str(column.server_default.arg).strip("'")
                    assert f"default{default}" in normalize(declaration).replace("'", "")
                else:
                    assert "DEFAULT" not in declaration
        for index in table.indexes:
            kind = "UNIQUE KEY" if index.unique else "KEY"
            expected = f"{kind} {index.name} ({', '.join(c.name for c in index.columns)})"
            assert normalize(expected) in normalize(body)
        for constraint in table.constraints:
            if isinstance(constraint, CheckConstraint):
                expression = str(
                    constraint.sqltext.compile(
                        dialect=mysql.dialect(),
                        compile_kwargs={"literal_binds": True, "include_table": False},
                    )
                )
                assert normalize(f"CONSTRAINT {constraint.name} CHECK ({expression})") in normalize(
                    body
                )
        for fk in table.foreign_key_constraints:
            target = next(iter(fk.elements)).target_fullname.replace(".", "(") + ")"
            expected = (
                f"CONSTRAINT {fk.name} FOREIGN KEY ({', '.join(fk.column_keys)}) "
                f"REFERENCES {target} ON DELETE RESTRICT ON UPDATE RESTRICT"
            )
            assert normalize(expected) in normalize(body)
    assert SQL.count("CREATE TABLE ") == 3
    assert SQL.count("CONSTRAINT ck_") == 12
    assert SQL.count("UNIQUE KEY ") == 7
    assert SQL.count("GENERATED ALWAYS") == 4
    assert SQL.count("CREATE TRIGGER ") == 3
    assert SQL.count("IF OLD.is_deleted=1 AND NEW.is_deleted=0 THEN") == 3
    assert SQL.count("IF NOT (OLD.id <=> NEW.id) THEN") == 3
