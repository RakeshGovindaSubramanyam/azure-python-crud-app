from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import pyodbc
from typing import List, Optional
from config import get_connection_string
from fastapi.responses import RedirectResponse


app = FastAPI(title="Azure Python CRUD API")

@app.get("/")
async def redirect_to_docs():
    return RedirectResponse(url='/docs')

# Database connection string from config
connection_string = get_connection_string()

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
def read_root():
    return {"AZURE-PYTHON-CRUD-APP": "Welcome to Azure Python CRUD API"}

@app.get("/items", response_model=List[Item])
def read_items():
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description FROM items")
        
        items = []
        for row in cursor.fetchall():
            items.append({
                "id": row[0],
                "name": row[1],
                "description": row[2]
            })
        
        cursor.close()
        conn.close()
        return items
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description FROM items WHERE id = ?", item_id)
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item with id {item_id} not found"
            )
            
        item = {
            "id": row[0],
            "name": row[1],
            "description": row[2]
        }
        
        cursor.close()
        conn.close()
        return item
    except pyodbc.Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@app.post("/items", response_model=Item, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO items (name, description) OUTPUT INSERTED.ID VALUES (?, ?)",
            item.name,
            item.description
        )
        
        new_id = cursor.fetchone()[0]
        conn.commit()
        
        # Fetch the created item
        cursor.execute("SELECT id, name, description FROM items WHERE id = ?", new_id)
        row = cursor.fetchone()
        
        created_item = {
            "id": row[0],
            "name": row[1],
            "description": row[2]
        }
        
        cursor.close()
        conn.close()
        return created_item
    except pyodbc.Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, item: ItemCreate):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Check if item exists
        cursor.execute("SELECT id FROM items WHERE id = ?", item_id)
        if not cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item with id {item_id} not found"
            )
        
        # Update the item
        cursor.execute(
            "UPDATE items SET name = ?, description = ? WHERE id = ?",
            item.name,
            item.description,
            item_id
        )
        conn.commit()
        
        # Fetch the updated item
        cursor.execute("SELECT id, name, description FROM items WHERE id = ?", item_id)
        row = cursor.fetchone()
        
        updated_item = {
            "id": row[0],
            "name": row[1],
            "description": row[2]
        }
        
        cursor.close()
        conn.close()
        return updated_item
    except pyodbc.Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Check if item exists
        cursor.execute("SELECT id FROM items WHERE id = ?", item_id)
        if not cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item with id {item_id} not found"
            )
        
        # Delete the item
        cursor.execute("DELETE FROM items WHERE id = ?", item_id)
        conn.commit()
        
        cursor.close()
        conn.close()
        return None
    except pyodbc.Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
