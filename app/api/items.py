from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.security import get_current_user
from app.schemas.item import *
from app.crud import item as crud_item

router = APIRouter(prefix="/items", tags=["Items"])


# ---------- CATEGORY ----------
@router.post("/categories", response_model=CategoryOut)
def add_category(
        data: CategoryCreate,
        db: Session = Depends(get_db),
        user=Depends(get_current_user)):
    return crud_item.create_category(db, data.name, data.description)


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(
        db: Session = Depends(get_db),
        user=Depends(get_current_user)):
    return crud_item.get_categories(db)


# ---------- ITEMS ----------
@router.post("/", response_model=ItemOut)
def add_item(
        data: ItemCreate,
        db: Session = Depends(get_db),
        user=Depends(get_current_user)):
    return crud_item.create_item(db, data)


@router.get("/", response_model=list[ItemOut])
def get_items(
        db: Session = Depends(get_db),
        user=Depends(get_current_user)):
    return crud_item.list_items(db)
# ---------- UPDATE ITEM ----------
@router.put("/{item_id}", response_model=ItemOut)
def edit_item(
        item_id: int,
        data: ItemUpdate,
        db: Session = Depends(get_db),
        user=Depends(get_current_user)):
    item = crud_item.update_item(db, item_id, data)
    if not item:
        raise HTTPException(404, "Item not found")
    return item


# ---------- DELETE ITEM ----------
@router.delete("/{item_id}")
def remove_item(
        item_id: int,
        db: Session = Depends(get_db),
        user=Depends(get_current_user)):
    ok = crud_item.delete_item(db, item_id)
    if not ok:
        raise HTTPException(404, "Item not found")
    return {"status": "deleted"}


# ---------- UPDATE CATEGORY ----------
@router.put("/categories/{cid}")
def edit_category(
        cid: int,
        data: CategoryUpdate,
        db: Session = Depends(get_db),
        user=Depends(get_current_user)):
    cat = crud_item.update_category(db, cid, data.name, data.description)
    if not cat:
        raise HTTPException(404, "Category not found")
    return cat


# ---------- DELETE CATEGORY ----------
@router.delete("/categories/{cid}")
def remove_category(
        cid: int,
        db: Session = Depends(get_db),
        user=Depends(get_current_user)):
    ok = crud_item.delete_category(db, cid)
    if not ok:
        raise HTTPException(404, "Category not found")
    return {"status": "deleted"}

@router.get("/search", response_model=list[ItemOut])
def search_items_endpoint(
        q: str = Query(..., min_length=1),
        db: Session = Depends(get_db),
        user=Depends(get_current_user)):
    return crud_item.search_items(db, q)


from app.models.all_models import Item

@router.get("/low-stock")
def low_stock(
        db: Session = Depends(get_db),
        user=Depends(get_current_user)):

    items = db.query(Item).filter(
        Item.stock_qty <= Item.reorder_level
    ).all()

    return items
