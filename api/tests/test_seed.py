from app.models import Organization, User


def test_seed_super_admin_idempotent(db):
    from app.seed_auth import seed_super_admin

    seed_super_admin(db)
    seed_super_admin(db)
    admins = db.query(User).filter(User.role == "super_admin").all()
    assert len(admins) == 1
    assert admins[0].org_id is None


def test_seed_demo_orgs_idempotent(db):
    from app.seed_auth import seed_demo_orgs

    seed_demo_orgs(db)
    seed_demo_orgs(db)
    assert db.query(Organization).count() == 2
    org_admins = db.query(User).filter(User.role == "org_admin").all()
    members = db.query(User).filter(User.role == "member").all()
    assert len(org_admins) == 2
    assert len(members) == 2
    assert all(u.must_change_password for u in org_admins)
    assert all(u.org_id is not None for u in org_admins + members)
