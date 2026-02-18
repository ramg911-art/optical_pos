from sqlalchemy.orm import Session
from app.models.all_models import Category, Item


# ---------- CATEGORY ----------
def create_category(db: Session, name: str):
    cat = Category(name=name)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


def get_categories(db: Session):
    return db.query(Category).all()


# ---------- ITEMS ----------
def create_item(db: Session, data):
    item = Item(**data.dict())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def list_items(db: Session):
    return db.query(Item).all()

# ---------- UPDATE ITEM ----------
def update_item(db: Session, item_id: int, data):
    item = db.query(Item).get(item_id)
    if not item:
        return None

    for key, value in data.dict(exclude_unset=True).items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return item


# ---------- DELETE ITEM ----------
def delete_item(db: Session, item_id: int):
    item = db.query(Item).get(item_id)
    if not item:
        return False

    db.delete(item)
    db.commit()
    return True


# ---------- CATEGORY UPDATE ----------
def update_category(db: Session, cid: int, name: str):
    cat = db.query(Category).get(cid)
    if not cat:
        return None

    cat.name = name
    db.commit()
    db.refresh(cat)
    return cat


# ---------- CATEGORY DELETE ----------
def delete_category(db: Session, cid: int):
    cat = db.query(Category).get(cid)
    if not cat:
        return False

    db.delete(cat)
    db.commit()
    return True

from sqlalchemy import or_
from app.models.all_models import Item


def search_items(db: Session, query: str, limit: int = 20):
    return (
        db.query(Item)
        .filter(
            or_(
                Item.name.ilike(f"%{query}%"),
                Item.brand.ilike(f"%{query}%"),
                Item.model.ilike(f"%{query}%"),
            )
        )
        .limit(limit)
        .all()
    )

