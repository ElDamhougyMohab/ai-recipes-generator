from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas
from app.database import get_db
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/meal-plans", response_model=schemas.MealPlan)
async def create_meal_plan(
    meal_plan: schemas.MealPlanCreate,
    db: Session = Depends(get_db)
):
    """Create a new meal plan"""
    try:
        logger.info(f"📅 Creating meal plan: {meal_plan.name}")
        
        # Validate that all recipe IDs exist
        all_recipe_ids = []
        for day_recipes in meal_plan.recipes.values():
            all_recipe_ids.extend(day_recipes)
        
        # Check if all recipes exist
        for recipe_id in all_recipe_ids:
            recipe = crud.get_recipe(db, recipe_id=recipe_id)
            if not recipe:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Recipe with ID {recipe_id} not found"
                )
        
        db_meal_plan = crud.create_meal_plan(db=db, meal_plan=meal_plan)
        logger.info(f"✅ Created meal plan with ID: {db_meal_plan.id}")
        return db_meal_plan
        
    except Exception as e:
        logger.error(f"❌ Error creating meal plan: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to create meal plan: {str(e)}")


@router.get("/meal-plans", response_model=schemas.PaginatedMealPlansResponse)
async def get_meal_plans(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db)
):
    """Get paginated list of meal plans"""
    try:
        logger.info(f"📋 Fetching meal plans - page {page}, size {page_size}")
        
        skip = (page - 1) * page_size
        meal_plans = crud.get_meal_plans(db, skip=skip, limit=page_size)
        total = crud.get_meal_plans_count(db)
        
        logger.info(f"✅ Retrieved {len(meal_plans)} meal plans (total: {total})")
        
        return schemas.PaginatedMealPlansResponse.paginate(
            items=meal_plans,
            total=total,
            page=page,
            per_page=page_size
        )
        
    except Exception as e:
        logger.error(f"❌ Error fetching meal plans: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch meal plans: {str(e)}")


@router.get("/meal-plans/{meal_plan_id}", response_model=schemas.MealPlan)
async def get_meal_plan(
    meal_plan_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific meal plan by ID"""
    try:
        logger.info(f"📅 Fetching meal plan with ID: {meal_plan_id}")
        
        meal_plan = crud.get_meal_plan(db, meal_plan_id=meal_plan_id)
        if meal_plan is None:
            logger.warning(f"❌ Meal plan not found: {meal_plan_id}")
            raise HTTPException(status_code=404, detail="Meal plan not found")
        
        logger.info(f"✅ Retrieved meal plan: {meal_plan.name}")
        return meal_plan
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching meal plan {meal_plan_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch meal plan: {str(e)}")


@router.delete("/meal-plans/{meal_plan_id}")
async def delete_meal_plan(
    meal_plan_id: int,
    db: Session = Depends(get_db)
):
    """Delete a meal plan"""
    try:
        logger.info(f"🗑️ Deleting meal plan with ID: {meal_plan_id}")
        
        meal_plan = crud.get_meal_plan(db, meal_plan_id=meal_plan_id)
        if meal_plan is None:
            logger.warning(f"❌ Meal plan not found: {meal_plan_id}")
            raise HTTPException(status_code=404, detail="Meal plan not found")
        
        crud.delete_meal_plan(db=db, meal_plan_id=meal_plan_id)
        logger.info(f"✅ Deleted meal plan: {meal_plan.name}")
        
        return {"message": "Meal plan deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting meal plan {meal_plan_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete meal plan: {str(e)}")
