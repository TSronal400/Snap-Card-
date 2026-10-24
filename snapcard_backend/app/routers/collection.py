from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Card, UserCollection
from app.schemas import CardResponse

router = APIRouter(prefix="/collection", tags=["Colección de Usuario"])

@router.get("", response_model=List[CardResponse])
def get_user_collection(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Obtener IDs de cartas en la colección del usuario
    collection_items = db.scalars(select(UserCollection).where(UserCollection.user_id == user.id)).all()
    card_ids = [item.card_id for item in collection_items]

    if not card_ids:
        return []

    cards = db.scalars(select(Card).where(Card.id.in_(card_ids))).all()
    return cards

@router.post("/add", status_code=status.HTTP_201_CREATED)
def add_card_to_collection(data: dict, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    card_id = data.get("card_id")
    if not card_id:
        raise HTTPException(status_code=400, detail="Se requiere el ID de la carta")

    card = db.get(Card, int(card_id))
    if not card:
        raise HTTPException(status_code=404, detail="Carta no encontrada en la base de datos")

    # Verificar si ya la tiene
    existing = db.scalar(
        select(UserCollection).where(
            UserCollection.user_id == user.id,
            UserCollection.card_id == card.id
        )
    )
    if existing:
        return {"message": "La carta ya está en tu colección", "card_id": card.id}

    item = UserCollection(user_id=user.id, card_id=card.id)
    db.add(item)
    db.commit()
    return {"message": "¡Carta añadida a tu colección con éxito!", "card_id": card.id, "card_name": card.name}
