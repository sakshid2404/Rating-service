from pydantic import BaseModel

class ratingcreate(BaseModel):
    business_id:int
    customer_id:int
    rating:int
    review: str | None = None 
    created_at:int
    
class ratingRead(ratingcreate):
    id: int
    
    
    