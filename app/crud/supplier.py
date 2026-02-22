from sqlalchemy.exc import SQLAlchemyError

from app.models.all_models import Supplier


def _safe_commit(db) -> None:
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise


def create_supplier(db, data):
    s = Supplier(**data.dict())
    db.add(s)
    _safe_commit(db)
    db.refresh(s)
    return s


def list_suppliers(db):
    return db.query(Supplier).all()


def delete_supplier(db, sid):
    s = db.query(Supplier).get(sid)
    if not s:
        return False
    db.delete(s)
    _safe_commit(db)
    return True
