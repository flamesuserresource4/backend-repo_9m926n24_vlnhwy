import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Item, LookRequest, LookJob

app = FastAPI(title="LookLab API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "LookLab Backend Running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response

# ---------------- Catalog Endpoints ----------------

@app.post("/api/items", response_model=dict)
def create_item(item: Item):
    try:
        item_id = create_document("item", item)
        return {"id": item_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/items", response_model=List[dict])
def list_items(category: Optional[str] = None, limit: int = 100):
    try:
        query = {"category": category} if category else {}
        items = get_documents("item", query, limit)
        # Convert ObjectId to string
        for it in items:
            if "_id" in it:
                it["id"] = str(it.pop("_id"))
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------- Look Generation (mock) ----------------

class LookStartResponse(BaseModel):
    job_id: str
    status: str

@app.post("/api/looks/start", response_model=LookStartResponse)
def start_look(req: LookRequest):
    """
    Starts a mock generation job. In a real system this would enqueue a task
    to a worker that calls an image model and optionally a video model.
    """
    try:
        job = LookJob(
            status="queued",
            user_image_url=req.user_image_url,
            selections={
                "top_id": req.top_id,
                "bottom_id": req.bottom_id,
                "shoes_id": req.shoes_id,
                "accessory_ids": req.accessory_ids or [],
                "background_id": req.background_id,
                "animate": req.animate,
            },
        )
        job_id = create_document("lookjob", job)
        return LookStartResponse(job_id=job_id, status="queued")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/looks", response_model=List[dict])
def list_looks(limit: int = 50):
    try:
        jobs = get_documents("lookjob", {}, limit)
        for j in jobs:
            if "_id" in j:
                j["id"] = str(j.pop("_id"))
        return jobs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
