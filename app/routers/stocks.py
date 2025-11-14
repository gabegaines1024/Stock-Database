from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import StockBase, Stock, StockUpdate
from app.crud import create_stock, get_stock, update_stock, delete_stock, list_stocks

router = APIRouter(prefix="/stocks", tags=["stocks"])

