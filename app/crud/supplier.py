from app.models.all_models import Supplier


def create_supplier(db, data):
    s = Supplier(**data.dict())
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def list_suppliers(db):
    return db.query(Supplier).all()


def delete_supplier(db, sid):
    s = db.query(Supplier).get(sid)
    db.delete(s)
    db.commit()
