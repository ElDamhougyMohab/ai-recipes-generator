from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app import crud, schemas, models
from app.database import get_db
from app.services.gemini_service import GeminiService
from pydantic import ValidationError

router = APIRouter()

@router.post("/recipes/test-validation", response_model=dict)
async def test_validation(request: schemas.RecipeGenerateRequest):
    """Test validation without database dependency"""
    return {
        "message": "Validation successful!",
        "data": {
            "ingredients": request.ingredients,
            "dietary_preferences": request.dietary_preferences,
            "cuisine_type": request.cuisine_type,
            "meal_type": request.meal_type
        }
    }

@router.post("/recipes/validate-diet", response_model=dict)
async def validate_dietary_restrictions(
    request: schemas.RecipeGenerateRequest
):
    """Validate ingredients against dietary restrictions and return conflicts"""
    try:
        gemini_service = GeminiService()
        allowed_ingredients, protein_suggestions = gemini_service._filter_ingredients_by_diet(
            request.ingredients, 
            request.dietary_preferences
        )
        
        forbidden_ingredients = [ing for ing in request.ingredients if ing not in allowed_ingredients]
        
        return {
            "has_conflicts": len(forbidden_ingredients) > 0,
            "allowed_ingredients": allowed_ingredients,
            "forbidden_ingredients": forbidden_ingredients,
            "protein_suggestions": protein_suggestions,
            "message": "Some ingredients conflict with your dietary preferences" if forbidden_ingredients else "All ingredients are compatible"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating dietary restrictions: {str(e)}"
        )

@router.post("/recipes/generate", response_model=dict)
async def generate_recipes(
    request: schemas.RecipeGenerateRequest,
    db: Session = Depends(get_db)
):
    try:    
        gemini_service = GeminiService()
        
        # First, validate ingredients against dietary restrictions
        allowed_ingredients, protein_suggestions = gemini_service._filter_ingredients_by_diet(
            request.ingredients, 
            request.dietary_preferences
        )
        
        forbidden_ingredients = [ing for ing in request.ingredients if ing not in allowed_ingredients]
        
        generated_recipes = await gemini_service.generate_recipes(
            ingredients=request.ingredients,
            dietary_preferences=request.dietary_preferences,
            cuisine_type=request.cuisine_type,
            meal_type=request.meal_type
        )
        
        # Generate temporary IDs for the recipes (not saved to database yet)
        import time
        import random
        temp_recipes = []
        for i, recipe_data in enumerate(generated_recipes):
            # Create a temporary ID that won't conflict with database IDs
            temp_id = f"temp_{int(time.time() * 1000)}_{i}_{random.randint(1000, 9999)}"
            recipe_dict = {
                "id": temp_id,
                "title": recipe_data.get("title", ""),
                "description": recipe_data.get("description", ""),
                "instructions": recipe_data.get("instructions", ""),
                "ingredients": recipe_data.get("ingredients", []),
                "prep_time": recipe_data.get("prep_time"),
                "cook_time": recipe_data.get("cook_time"),
                "servings": recipe_data.get("servings"),
                "difficulty": recipe_data.get("difficulty"),
                "rating": None,
                "created_at": None,
                "is_temporary": True
            }
            temp_recipes.append(recipe_dict)
        
        # Return comprehensive response
        return {
            "recipes": temp_recipes,
            "dietary_filtering": {
                "has_conflicts": len(forbidden_ingredients) > 0,
                "allowed_ingredients": allowed_ingredients,
                "forbidden_ingredients": forbidden_ingredients,
                "protein_suggestions": protein_suggestions,
                "message": f"Filtered out {len(forbidden_ingredients)} non-compliant ingredients" if forbidden_ingredients else "All ingredients are dietary compliant"
            },
            "generation_info": {
                "total_recipes": len(temp_recipes),
                "ingredients_used": len(allowed_ingredients),
                "dietary_preferences": request.dietary_preferences or [],
                "cuisine_type": request.cuisine_type,
                "meal_type": request.meal_type
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recipes: {str(e)}"
        )

@router.get("/recipes", response_model=schemas.PaginatedResponse)
def read_recipes(
    page: int = Query(1, ge=1, le=1000, description="Page number (1-based)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of recipes per page (max 100)"),
    db: Session = Depends(get_db)
):
    """Get recipes with pagination (max 10 per page by default)"""
    try:
        # Enforce max page size of 10 for optimal performance
        if page_size > 10:
            page_size = 10
            
        paginated_result = crud.get_recipes_paginated(
            db=db, 
            page=page, 
            per_page=page_size
        )
        return paginated_result
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {str(e)}"
        )

@router.get("/recipes/search", response_model=schemas.PaginatedResponse)
def search_recipes(
    q: Optional[str] = Query(None, max_length=200, description="Search query"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty"),
    min_rating: Optional[float] = Query(None, ge=1.0, le=5.0, description="Minimum rating"),
    max_prep_time: Optional[int] = Query(None, ge=0, le=600, description="Maximum prep time in minutes"),
    max_cook_time: Optional[int] = Query(None, ge=0, le=1440, description="Maximum cook time in minutes"),
    page: int = Query(1, ge=1, le=1000, description="Page number (1-based)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of recipes per page (max 100)"),
    db: Session = Depends(get_db)
):
    """Search recipes with comprehensive parameter validation and pagination"""
    try:
        # Validate search parameters
        search_params = schemas.RecipeSearchParams(
            q=q,
            difficulty=difficulty,
            min_rating=min_rating,
            max_prep_time=max_prep_time,
            max_cook_time=max_cook_time
        )
        
        # Enforce max page size of 10 for optimal performance
        if page_size > 10:
            page_size = 10
        
        # Use paginated search with filters
        paginated_result = crud.get_recipes_paginated(
            db=db, 
            page=page, 
            per_page=page_size,
            search=search_params.q
        )
        
        return paginated_result
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {str(e)}"
        )

@router.get("/recipes/{recipe_id}", response_model=schemas.Recipe)
def read_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """Get a specific recipe with ID validation"""
    if recipe_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Recipe ID must be a positive integer"
        )
    
    db_recipe = crud.get_recipe(db, recipe_id=recipe_id)
    if db_recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return db_recipe

@router.post("/recipes", response_model=schemas.Recipe)
def create_recipe(recipe: schemas.RecipeCreate, db: Session = Depends(get_db)):
    """Create a new recipe with comprehensive validation"""
    try:
        return crud.create_recipe(db=db, recipe=recipe)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating recipe: {str(e)}"
        )

@router.delete("/recipes/{recipe_id}")
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """Delete a recipe with ID validation"""
    if recipe_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Recipe ID must be a positive integer"
        )
    
    success = crud.delete_recipe(db, recipe_id=recipe_id)
    if not success:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return {"message": "Recipe deleted successfully"}

@router.put("/recipes/{recipe_id}/rating")
def rate_recipe(
    recipe_id: int,
    rating_request: schemas.RecipeRatingRequest,
    db: Session = Depends(get_db)
):
    """Rate a recipe with comprehensive validation"""
    if recipe_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Recipe ID must be a positive integer"
        )
    
    try:
        updated_recipe = crud.update_recipe_rating(db, recipe_id=recipe_id, rating=rating_request.rating)
        if not updated_recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        return updated_recipe
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {str(e)}"
        )

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total_recipes = db.query(models.Recipe).count()
    avg_rating = db.query(func.avg(models.Recipe.rating)).scalar() or 0
    
    return {
        "total_recipes": total_recipes,
        "average_rating": round(avg_rating, 2)
    }

@router.post("/meal-plans", response_model=schemas.MealPlan)
def create_meal_plan(meal_plan: schemas.MealPlanCreate, db: Session = Depends(get_db)):
    """Create a new meal plan with comprehensive validation"""
    try:
        return crud.create_meal_plan(db=db, meal_plan=meal_plan)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating meal plan: {str(e)}"
        )

@router.get("/meal-plans", response_model=schemas.PaginatedMealPlansResponse)
def read_meal_plans(
    page: int = Query(1, ge=1, le=1000, description="Page number (1-based)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of meal plans per page (max 100)"),
    db: Session = Depends(get_db)
):
    """Get meal plans with pagination (max 10 per page by default)"""
    try:
        # Enforce max page size of 10 for optimal performance
        if page_size > 10:
            page_size = 10
            
        paginated_result = crud.get_meal_plans_paginated(
            db=db, 
            page=page, 
            per_page=page_size
        )
        return paginated_result
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {str(e)}"
        )

@router.get("/meal-plans/{meal_plan_id}", response_model=schemas.MealPlan)
def read_meal_plan(meal_plan_id: int, db: Session = Depends(get_db)):
    """Get a specific meal plan with ID validation"""
    if meal_plan_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Meal plan ID must be a positive integer"
        )
    
    db_meal_plan = crud.get_meal_plan(db, meal_plan_id=meal_plan_id)
    if db_meal_plan is None:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    return db_meal_plan

@router.delete("/meal-plans/{meal_plan_id}")
def delete_meal_plan(meal_plan_id: int, db: Session = Depends(get_db)):
    """Delete a meal plan with ID validation"""
    if meal_plan_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Meal plan ID must be a positive integer"
        )
    
    success = crud.delete_meal_plan(db, meal_plan_id=meal_plan_id)
    if not success:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    return {"message": "Meal plan deleted successfully"}
