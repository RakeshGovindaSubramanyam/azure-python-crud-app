from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List
from fastapi.responses import RedirectResponse

app = FastAPI(title="In-Memory CRUD API")

# In-memory storage
items_db = []
item_id_counter = 1

class ItemBase(BaseModel):
    name: str
    description: str

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    
    class Config:
        orm_mode = True

@app.get("/")
async def redirect_to_docs():
    return RedirectResponse(url='/docs')

@app.get("/items", response_model=List[Item])
def read_items():
    return items_db

@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int):
    item = next((item for item in items_db if item["id"] == item_id), None)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    return item

@app.post("/items", response_model=Item, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate):
    global item_id_counter
    new_item = {
        "id": item_id_counter,
        "name": item.name,
        "description": item.description
    }
    items_db.append(new_item)
    item_id_counter += 1
    return new_item

@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, item: ItemCreate):
    item_index = next((index for index, item in enumerate(items_db) if item["id"] == item_id), None)
    if item_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    
    updated_item = {
        "id": item_id,
        "name": item.name,
        "description": item.description
    }
    items_db[item_index] = updated_item
    return updated_item

@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int):
    item_index = next((index for index, item in enumerate(items_db) if item["id"] == item_id), None)
    if item_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    
    items_db.pop(item_index)
    return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
