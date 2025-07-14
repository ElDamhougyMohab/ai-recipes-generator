from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import logging

from app.database import get_db
from app.models import Recipe
from app.schemas import RecipeCreate, Recipe as RecipeSchema, RecipeGenerateResponse, PaginatedResponse
from app.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/recipes", response_model=PaginatedResponse)
async def get_recipes(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db)
):
    """Get recipes with pagination"""
    try:
        # Validate pagination parameters
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 10
            
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get total count
        total = db.query(Recipe).count()
        
        # Get paginated recipes
        recipes = db.query(Recipe).offset(offset).limit(page_size).all()
        
        # Return paginated response
        return PaginatedResponse.paginate(recipes, total, page, page_size)
        
    except Exception as e:
        logger.error(f"Error getting recipes: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch recipes")

@router.post("/recipes", response_model=RecipeSchema)
async def create_recipe(recipe: RecipeCreate, db: Session = Depends(get_db)):
    """Create a new recipe"""
    try:
        db_recipe = Recipe(**recipe.dict())
        db.add(db_recipe)
        db.commit()
        db.refresh(db_recipe)
        return db_recipe
    except Exception as e:
        logger.error(f"Error creating recipe: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create recipe")

@router.post("/recipes/generate", response_model=RecipeGenerateResponse)
async def generate_recipe(
    request: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate a recipe using Gemini AI and save it to the database"""
    try:
        ingredients = request.get("ingredients", [])
        dietary_restrictions = request.get("dietary_restrictions", [])
        
        if not ingredients:
            raise HTTPException(status_code=400, detail="Ingredients are required")
        
        # Generate recipe using async Gemini service
        gemini_service = GeminiService()
        
        # Generate the recipe asynchronously
        recipe_list = await gemini_service.generate_recipes(
            ingredients=ingredients,
            dietary_preferences=dietary_restrictions
        )
        
        # Check if we got recipes
        if not recipe_list:
            raise HTTPException(status_code=500, detail="No recipes generated")
        
        # Save all generated recipes to database
        saved_recipes = []
        for recipe_data in recipe_list:
            db_recipe = Recipe(
                title=recipe_data["title"],
                description=recipe_data.get("description", ""),
                ingredients=recipe_data["ingredients"],
                instructions=recipe_data["instructions"],
                prep_time=recipe_data.get("prep_time", 20),
                cook_time=recipe_data.get("cook_time", 30),
                servings=recipe_data.get("servings", 4),
                difficulty=recipe_data.get("difficulty", "Medium")
            )
            
            db.add(db_recipe)
            saved_recipes.append(db_recipe)
        
        db.commit()
        
        # Refresh all saved recipes to get their IDs
        for db_recipe in saved_recipes:
            db.refresh(db_recipe)
            logger.info(f"Generated and saved recipe: {db_recipe.title}")
        
        # Return all generated recipes
        return RecipeGenerateResponse(recipes=saved_recipes)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating recipe: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate recipe: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Recipe service is running"}
