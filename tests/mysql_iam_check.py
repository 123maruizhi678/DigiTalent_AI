"""IAM 数据库行为验收；显式授权入口，复用独立 MySQL 连接与回滚。"""

from uuid import uuid4

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.orm import Session

from app.models.iam import Organization, User, UserOrganization
from tests import mysql_orm_check


@pytest.fixture
def database(request):
    yield from mysql_orm_check.database.__wrapped__(request)


def user(**values):
    return User(username=uuid4().hex, real_name="测试用户", **values)


def organization():
    return Organization(
        organization_code=uuid4().hex, organization_name="测试组织", organization_type="company"
    )


def test_relationship_generated_defaults(database):
    with Session(database) as session:
        account, org = user(), organization()
        session.add_all([account, org])
        session.flush()
        link = UserOrganization(user_id=account.id, organization_id=org.id, is_primary=True)
        session.add(link)
        session.flush()
        session.expire_all()
        assert account.status == "inactive"
        assert account.active_key == org.active_key == link.active_key == 1
        assert link.primary_user_id == account.id.hex
        result = session.execute(
            select(User, Organization)
            .join(UserOrganization, UserOrganization.user_id == User.id)
            .join(Organization, Organization.id == UserOrganization.organization_id)
        ).one()
        assert result == (account, org)
        link.is_deleted = True
        session.flush()
        session.refresh(link)
        assert link.active_key is None and link.primary_user_id is None


@pytest.mark.parametrize(
    "field,value",
    [("status", "bad"), ("is_deleted", 2), ("email", "UPPER@example.com"), ("username", " ")],
)
def test_user_checks(database, field, value):
    with Session(database) as session:
        row = user()
        session.add(row)
        session.flush()
        with pytest.raises(IntegrityError), session.begin_nested():
            session.execute(
                text(f"UPDATE sys_user SET {field}=:value WHERE id=:id"),
                {"value": value, "id": row.id.hex},
            )


def test_uniqueness_history_and_primary(database):
    with Session(database) as session:
        row, org, other = user(), organization(), organization()
        session.add_all([row, org, other])
        session.flush()
        with pytest.raises(IntegrityError), session.begin_nested():
            session.add(User(username=row.username, real_name="重复"))
            session.flush()
        session.add(UserOrganization(user_id=row.id, organization_id=org.id, is_primary=True))
        session.flush()
        with pytest.raises(IntegrityError), session.begin_nested():
            session.add(UserOrganization(user_id=row.id, organization_id=other.id, is_primary=True))
            session.flush()
        row.is_deleted = True
        session.flush()
        session.add(User(username=row.username, real_name="重新创建"))
        session.flush()


def test_foreign_key_rejects_missing_parent(database):
    with Session(database) as session:
        row = organization()
        row.parent_id = uuid4()
        with pytest.raises(IntegrityError), session.begin_nested():
            session.add(row)
            session.flush()


@pytest.mark.parametrize("table", ["sys_user", "sys_organization", "sys_user_organization"])
def test_three_triggers(database, table):
    with Session(database) as session:
        account, org = user(), organization()
        session.add_all([account, org])
        session.flush()
        link = UserOrganization(user_id=account.id, organization_id=org.id)
        session.add(link)
        session.flush()
        row = {"sys_user": account, "sys_organization": org, "sys_user_organization": link}[table]
        for statement, params in [
            (f"UPDATE {table} SET id=:new_id WHERE id=:id", {"new_id": uuid4().hex}),
        ]:
            with pytest.raises(DBAPIError, match="immutable"), session.begin_nested():
                session.execute(text(statement), {"id": row.id.hex, **params})
        row.is_deleted = True
        session.flush()
        with pytest.raises(DBAPIError, match="cannot be restored"), session.begin_nested():
            session.execute(
                text(f"UPDATE {table} SET is_deleted=0 WHERE id=:id"), {"id": row.id.hex}
            )
