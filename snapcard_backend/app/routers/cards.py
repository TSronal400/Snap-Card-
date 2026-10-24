from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Card
from app.schemas import CardResponse, CardCreateRequest

router = APIRouter(prefix="/cards", tags=["Cartas"])

@router.get("/search", response_model=List[CardResponse])
def search_cards(
    q: Optional[str] = Query(None, description="Término de búsqueda por nombre o categoría"),
    category: Optional[str] = Query(None, description="Filtrar por categoría específica"),
    db: Session = Depends(get_db),
):
    stmt = select(Card)

    if q and q.strip():
        search_term = f"%{q.strip().lower()}%"
        stmt = stmt.where(
            or_(
                Card.name.ilike(search_term),
                Card.category.ilike(search_term),
                Card.element_type.ilike(search_term),
                Card.description.ilike(search_term),
            )
        )

    if category and category.strip() and category.lower() != "todas":
        stmt = stmt.where(Card.category.ilike(category.strip()))

    cards = db.scalars(stmt).all()
    return cards

@router.get("/", response_model=List[CardResponse])
def get_all_cards(db: Session = Depends(get_db)):
    cards = db.scalars(select(Card)).all()
    return cards

@router.get("/categories", response_model=List[String] if False else List[str])
def get_categories(db: Session = Depends(get_db)):
    categories = db.scalars(select(Card.category).distinct()).all()
    return list(categories)

@router.post("/", response_model=CardResponse, status_code=status.HTTP_201_CREATED)
def create_card(data: CardCreateRequest, db: Session = Depends(get_db)):
    card = Card(
        name=data.name.strip(),
        category=data.category.strip(),
        price=data.price,
        element_type=data.element_type.strip(),
        description=data.description.strip() if data.description else "",
        image_url=data.image_url.strip() if data.image_url else "",
    )
    db.add(card)
    db.commit()
    db.refresh(card)
    return card
