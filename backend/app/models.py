from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, Float
from sqlalchemy.sql import func
from app.database import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    instructions = Column(Text, nullable=False)
    ingredients = Column(JSON, nullable=False)
    prep_time = Column(Integer)  # in minutes
    cook_time = Column(Integer)  # in minutes
    servings = Column(Integer)
    difficulty = Column(String(50))
    rating = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class MealPlan(Base):
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    week_start = Column(DateTime)
    recipes = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
