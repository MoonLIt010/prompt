# from fastapi import FastAPI, HTTPException, Depends
# from pydantic import BaseModel
# from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey
# from sqlalchemy.orm import declarative_base, sessionmaker, relationship
# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
# from sqlalchemy.future import select
# from databases import Database
# from typing import List
# import uvicorn

# # Database connection configuration (MySQL setup)
# DATABASE_URL = "mysql+mysqlconnector://root:123@127.0.0.1:3306/virtual_clothes"
# database = Database(DATABASE_URL)

# # FastAPI instance
# app = FastAPI()

# # SQLAlchemy Base and session configuration
# Base = declarative_base()

# # Models for SQLAlchemy
# class Product(Base):
#     __tablename__ = "products"
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(255), nullable=False)
#     description = Column(String(255), nullable=True)
#     price = Column(Integer)
#     quantity = Column(Integer)
#     sold = Column(Integer)
#     label = Column(String(255))

#     images = relationship("Image", back_populates="product")
#     categories = relationship("Category", secondary="cat_product", back_populates="products")

# class Image(Base):
#     __tablename__ = "images"
#     id = Column(Integer, primary_key=True, index=True)
#     product_id = Column(Integer, ForeignKey('products.id'))
#     path = Column(String(255))

#     product = relationship("Product", back_populates="images")

# class Category(Base):
#     __tablename__ = "categories"
#     id = Column(Integer, primary_key=True, index=True)
#     en_name = Column(String(255))
#     ar_name = Column(String(255))

#     products = relationship("Product", secondary="cat_product", back_populates="categories")

# class Evaluation(Base):
#     __tablename__ = "evaluations"
#     id = Column(Integer, primary_key=True, index=True)
#     product_id = Column(Integer, ForeignKey('products.id'))
#     user_id = Column(Integer, ForeignKey('users.id'))
#     value = Column(String(255))

# # Pydantic models for response
# class ImageResponse(BaseModel):
#     id: int
#     path: str

# class CategoryResponse(BaseModel):
#     id: int
#     en_name: str
#     ar_name: str

# class ProductResponse(BaseModel):
#     id: int
#     name: str
#     description: str
#     price: int
#     quantity: int
#     sold: int
#     label: str
#     images: List[ImageResponse]
#     categories: List[CategoryResponse]

#     class Config:
#         orm_mode = True

# class EvaluationResponse(BaseModel):
#     id: int
#     product_id: int
#     user_id: int
#     value: str

#     class Config:
#         orm_mode = True

# # Dependency for database session
# async def get_db():
#     async with database as session:
#         yield session

# # Endpoint to get all projects (products)
# @app.get("/projects", response_model=List[ProductResponse])
# async def get_projects(db: Database = Depends(get_db)):
#     query = """
#     SELECT p.*, 
#            (SELECT JSON_ARRAYAGG(JSON_OBJECT('id', i.id, 'path', i.path)) 
#             FROM images i WHERE i.product_id = p.id) as images,
#            (SELECT JSON_ARRAYAGG(JSON_OBJECT('id', c.id, 'en_name', c.en_name, 'ar_name', c.ar_name))
#             FROM categories c
#             JOIN cat_product cp ON cp.category_id = c.id
#             WHERE cp.product_id = p.id) as categories
#     FROM products p;
#     """
#     products = await db.fetch_all(query)
#     return products

# # Endpoint to get all evaluations
# @app.get("/evaluations", response_model=List[EvaluationResponse])
# async def get_evaluations(db: Database = Depends(get_db)):
#     query = "SELECT * FROM evaluations"
#     evaluations = await db.fetch_all(query)
#     return evaluations

# # Manage database connection lifecycle
# @app.on_event("startup")
# async def startup():
#     await database.connect()

# @app.on_event("shutdown")
# async def shutdown():
#     await database.disconnect()

# if __name__ == "__main__":
#     uvicorn.run("api_routes:app", host="127.0.0.1", port=8000, reload=True)


from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from databases import Database
from typing import List
from contextlib import asynccontextmanager

DATABASE_URL = "mysql+mysqlconnector://root:@127.0.0.1:3306/virtual_clothes"
database = Database(DATABASE_URL)

Base = declarative_base()

app = FastAPI()

# Define lifespan context
@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()

app = FastAPI(lifespan=lifespan)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    price = Column(Integer)
    quantity = Column(Integer)
    sold = Column(Integer)
    label = Column(String(255))

    images = relationship("Image", back_populates="product")
    categories = relationship("Category", secondary="cat_product", back_populates="products")

class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    path = Column(String(255))

    product = relationship("Product", back_populates="images")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    en_name = Column(String(255))
    ar_name = Column(String(255))

    products = relationship("Product", secondary="cat_product", back_populates="categories")

class Evaluation(Base):
    __tablename__ = "evaluations"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    value = Column(String(255))

class ImageResponse(BaseModel):
    id: int
    path: str

class CategoryResponse(BaseModel):
    id: int
    en_name: str
    ar_name: str

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: int
    quantity: int
    sold: int
    label: str
    images: List[ImageResponse]
    categories: List[CategoryResponse]

    class Config:
        from_attributes = True  

class EvaluationResponse(BaseModel):
    id: int
    product_id: int
    user_id: int
    value: str

    class Config:
        from_attributes = True  

async def get_db():
    async with database as session:
        yield session

@app.get("/projects", response_model=List[ProductResponse])
async def get_projects(db: Database = Depends(get_db)):
    query = """
    SELECT p.*, 
           (SELECT JSON_ARRAYAGG(JSON_OBJECT('id', i.id, 'path', i.path)) 
            FROM images i WHERE i.product_id = p.id) as images,
           (SELECT JSON_ARRAYAGG(JSON_OBJECT('id', c.id, 'en_name', c.en_name, 'ar_name', c.ar_name))
            FROM categories c
            JOIN cat_product cp ON cp.category_id = c.id
            WHERE cp.product_id = p.id) as categories
    FROM products p;
    """
    products = await db.fetch_all(query)
    print(products)  
    return products

@app.get("/evaluations", response_model=List[EvaluationResponse])
async def get_evaluations(db: Database = Depends(get_db)):
    query = "SELECT * FROM evaluations"
    evaluations = await db.fetch_all(query)
    print(evaluations)  
    return evaluations

@app.get("/highest_evaluation", response_model=EvaluationResponse)
async def get_highest_evaluation(db: Database = Depends(get_db)):
    query = """
    SELECT * 
    FROM evaluations
    WHERE value = (SELECT MAX(value) FROM evaluations)
    """
    highest_evaluation = await db.fetch_one(query)
    print(highest_evaluation)  
    return highest_evaluation
