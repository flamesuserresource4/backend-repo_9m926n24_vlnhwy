"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Literal

# -------------------- LookLab Schemas --------------------

Category = Literal["top", "bottom", "accessory", "shoes", "background"]

class Item(BaseModel):
    """
    Catalog items for try-on
    Collection name: "item"
    """
    name: str = Field(..., description="Display name")
    brand: Optional[str] = Field(None, description="Brand label")
    category: Category = Field(..., description="Item category")
    price: Optional[float] = Field(None, ge=0, description="Price in dollars")
    image_url: HttpUrl = Field(..., description="Preview image URL")
    color: Optional[str] = Field(None, description="Color descriptor")

class LookRequest(BaseModel):
    """
    User selection to generate a composite look
    Not a collection, used for request validation
    """
    user_image_url: HttpUrl
    top_id: Optional[str] = None
    bottom_id: Optional[str] = None
    shoes_id: Optional[str] = None
    accessory_ids: Optional[List[str]] = None
    background_id: Optional[str] = None
    animate: bool = False

class LookJob(BaseModel):
    """
    Generation jobs and results
    Collection name: "lookjob"
    """
    status: Literal["queued", "processing", "completed", "failed"] = "queued"
    user_image_url: HttpUrl
    selections: dict = Field(default_factory=dict)
    output_image_url: Optional[HttpUrl] = None
    output_video_url: Optional[HttpUrl] = None
    error: Optional[str] = None

# -------------------- Example legacy schemas (kept) --------------------

class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
