from datetime import date
from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models
from app.database import get_db, engine
from app.schemas import ratingRead, ratingcreate

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/bz/ratings/", response_model=list[ratingRead])
def read_business_ratings(
    limit: int = 10,
    date_from: date | None = Query(None, description="Filter ratings created after this date"),
    date_to: date | None = Query(None, description="Filter ratings created before this date"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Rating)

    if date_from:
        query = query.filter(models.Rating.created_at >= date_from)

    if date_to:
        query = query.filter(models.Rating.created_at <= date_to)

    return query.limit(limit).all()



@app.get("/bz/ratings/avg")
def get_business_avg_rating(business_id: int, db: Session = Depends(get_db)):
    result = db.query(
        func.avg(models.Rating.rating).label("average_rating"),
        func.count(models.Rating.id).label("total_ratings")
    ).filter(models.Rating.business_id == business_id).first()

    if result.total_ratings == 0:
        return {
            "business_id": business_id,
            "average_rating": 0,
            "total_ratings": 0
        }

    return {
        "business_id": business_id,
        "average_rating": round(result.average_rating, 2),
        "total_ratings": result.total_ratings
    }



@app.get("/cx/ratings/", response_model=list[ratingRead])
def read_customer_ratings(int = 0, limit: int = 10, db: Session = Depends(get_db)):
    ratings = db.query(models.Rating).limit(limit).all()
    return ratings


@app.post("/cx/ratings/create", response_model=ratingRead)
def create_customer_rating(rating: ratingcreate, db: Session = Depends(get_db)):
    new_rating = models.Rating(
        business_id=rating.business_id,
        customer_id=rating.customer_id,
        rating=rating.rating,
        review=rating.review
    )
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    return new_rating


@app.put("/cx/ratings/{id}/", response_model=ratingRead)
def update_customer_rating(id: int, rating: ratingcreate, db: Session = Depends(get_db)):
    rating_obj = db.query(models.Rating).filter(models.Rating.id == id).first()

    if not rating_obj:
        raise HTTPException(status_code=404, detail="Rating not found")

    rating_obj.business_id = rating.business_id
    rating_obj.customer_id = rating.customer_id
    rating_obj.rating = rating.rating
    rating_obj.review = rating.review

    db.commit()
    db.refresh(rating_obj)
    return rating_obj


@app.delete("/cx/ratings/{id}/")
def delete_customer_rating(id: int, db: Session = Depends(get_db)):
    rating_obj = db.query(models.Rating).filter(models.Rating.id == id).first()

    if not rating_obj:
        raise HTTPException(status_code=404, detail="Rating not found")

    db.delete(rating_obj)
    db.commit()
    return {"message": "Rating deleted successfully"}
