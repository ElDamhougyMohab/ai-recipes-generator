from sqlalchemy.orm import Session
from app import models, schemas
from typing import List, Optional


def get_recipe(db: Session, recipe_id: int):
    return db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()


def get_recipes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Recipe).offset(skip).limit(limit).all()


def create_recipe(db: Session, recipe: schemas.RecipeCreate):
    db_recipe = models.Recipe(**recipe.dict())
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return db_recipe


def delete_recipe(db: Session, recipe_id: int):
    db_recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if db_recipe:
        db.delete(db_recipe)
        db.commit()
        return True
    return False


def update_recipe_rating(db: Session, recipe_id: int, rating: float):
    db_recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if db_recipe:
        db_recipe.rating = rating
        db.commit()
        db.refresh(db_recipe)
        return db_recipe
    return None


def create_meal_plan(db: Session, meal_plan: schemas.MealPlanCreate):
    db_meal_plan = models.MealPlan(**meal_plan.dict())
    db.add(db_meal_plan)
    db.commit()
    db.refresh(db_meal_plan)
    return db_meal_plan


def get_meal_plans(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.MealPlan).offset(skip).limit(limit).all()


def get_meal_plan(db: Session, meal_plan_id: int):
    return db.query(models.MealPlan).filter(models.MealPlan.id == meal_plan_id).first()


def delete_meal_plan(db: Session, meal_plan_id: int):
    db_meal_plan = (
        db.query(models.MealPlan).filter(models.MealPlan.id == meal_plan_id).first()
    )
    if db_meal_plan:
        db.delete(db_meal_plan)
        db.commit()
        return True
    return False


def get_meal_plans_count(db: Session):
    """Get total count of meal plans"""
    return db.query(models.MealPlan).count()


def get_recipes_paginated(
    db: Session, page: int = 1, per_page: int = 10, search: Optional[str] = None
):
    """
    Get paginated recipes with optional search
    """
    from sqlalchemy import func, or_
    from app import schemas

    # Start with base query
    query = db.query(models.Recipe)

    # Apply search filter if provided
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                models.Recipe.title.ilike(search_term),
                models.Recipe.description.ilike(search_term),
            )
        )

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * per_page
    recipes = query.offset(offset).limit(per_page).all()

    # Create paginated response
    total_pages = (total + per_page - 1) // per_page

    return schemas.PaginatedResponse(
        items=recipes,
        total=total,
        page=page,
        pages=total_pages,
        per_page=per_page,
        has_next=page < total_pages,
        has_prev=page > 1,
    )


def get_meal_plans_paginated(db: Session, page: int = 1, per_page: int = 10):
    """
    Get paginated meal plans
    """
    from app import schemas

    # Get total count
    total = db.query(models.MealPlan).count()

    # Apply pagination
    offset = (page - 1) * per_page
    meal_plans = db.query(models.MealPlan).offset(offset).limit(per_page).all()

    # Create paginated response
    total_pages = (total + per_page - 1) // per_page

    return schemas.PaginatedMealPlansResponse(
        items=meal_plans,
        total=total,
        page=page,
        pages=total_pages,
        per_page=per_page,
        has_next=page < total_pages,
        has_prev=page > 1,
    )
