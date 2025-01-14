import os
import uvicorn
from pydantic import BaseModel, Field
from typing import Optional, List

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter


if os.getenv('API_ENV') != 'production':
    from dotenv import load_dotenv
    load_dotenv()


# ENV to vars
project_id = os.environ.get('PROJECT_ID', 'nuttee-lab-00')
location = os.environ.get('LOCATION', 'us-central1')
firestore_database = os.environ.get('FIRESTORE_DATABASE')
firestore_collection = os.environ.get('FIRESTORE_COLLECTION')

# Initialize Firestore

db = firestore.Client(
    project=project_id,
    database=firestore_database
)
orders_ref = db.collection(firestore_collection)

# FastAPI app

app = FastAPI()
app.project_id = project_id
app.location = location

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

class OrdersQueryPayload(BaseModel):
    member_id: str = Field(description="User's Member ID")

@app.post("/orders")
async def query_orders_by_member_id(
    payload: OrdersQueryPayload
) -> str:
    """Use this tool to retrieve customer orders information by queries Firestore collection "orders" with filter memberId.

    Args:
        member_id: The member ID to filter by.

    Returns:
        A list of dictionaries representing the queried orders.
    """
    query_ref = orders_ref.where(filter=FieldFilter("memberId", "==", payload.member_id))
    results = []
    for item in query_ref.get():
        results.append(item.to_dict())
    return str(results)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
