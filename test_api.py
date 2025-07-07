from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel 
test_api=FastAPI()



class DataQuery(BaseModel):
    price:int
    weight:int


class TaxQuery(BaseModel):
    netto:float
    tax_rate:float

@test_api.post("/test/count_tax")
def count_tax(taxQuery:TaxQuery):
        
            
        brutto=taxQuery.netto*(1+taxQuery.tax_rate)
       
            
        return {brutto}

@test_api.post("/price/ask")
def get_price(data:DataQuery):
    return{data.price,data.weight}
@test_api.get("/pytanie")
def data():
    return {"message": "jest ok data "}

books={"title":"John","author":"Doe"}
@test_api.get("/books")
def get_books():
     
          
    book1=books["title"]
          
    return {book1}


produkts=[
     {"name":"laptop","price":1000,"category":"electronics"},
     {"name":"telefon","price":500,"category":"electronics"}
]
@test_api.get("/products")
def get_products(price:Optional[int]=None,name:Optional[str]=None):
     if price:
        filtered = [produkt for produkt in produkts if produkt["price"]<500.00]
        return filtered
    

     if name:
          filtered = [produkt for produkt in produkts if produkt["name"]==name]
          return filtered   
     return produkts,name                
     