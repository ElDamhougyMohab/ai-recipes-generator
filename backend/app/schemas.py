from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import re

class IngredientSchema(BaseModel):
    """Schema for individual ingredient validation"""
    name: str = Field(..., min_length=1, max_length=100, description="Ingredient name")
    amount: Optional[Union[int, float, str]] = Field(None, description="Amount of ingredient")
    unit: Optional[str] = Field(None, max_length=50, description="Unit of measurement")
    notes: Optional[str] = Field(None, max_length=100, description="Additional notes")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Ingredient name cannot be empty')
        # Remove extra whitespace and validate format
        clean_name = re.sub(r'\s+', ' ', v.strip())
        # Allow Unicode letters, numbers, spaces, and common punctuation for international ingredients
        if not re.match(r'^[\w\s\-\'\.()&,:]+$', clean_name, re.UNICODE):
            raise ValueError('Ingredient name contains invalid characters')
        return clean_name
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v is None:
            return v
        if isinstance(v, (int, float)):
            return v
        if isinstance(v, str):
            # Handle string amounts like "1/2", "to taste", etc.
            v = v.strip()
            if not v:
                return None
            # Allow common text amounts
            if v.lower() in ['to taste', 'as needed', 'optional', 'for garnish']:
                return v
            # Try to parse fractions or numbers
            try:
                if '/' in v:
                    parts = v.split('/')
                    if len(parts) == 2:
                        return float(parts[0]) / float(parts[1])
                return float(v)
            except (ValueError, ZeroDivisionError):
                return v  # Return as string if can't parse
        return v
    
    @field_validator('unit')
    @classmethod
    def validate_unit(cls, v):
        if v is None or v == "":
            return v
        # More flexible unit validation - allow any reasonable unit
        v = v.strip()
        if not v:
            return v
        # Just clean up the unit, don't restrict too much
        clean_unit = re.sub(r'\s+', ' ', v.strip())
        return clean_unit

class RecipeBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200, description="Recipe title")
    description: Optional[str] = Field(None, max_length=1000, description="Recipe description")
    instructions: Union[str, List[str]] = Field(..., description="Cooking instructions")
    ingredients: List[IngredientSchema] = Field(..., min_items=1, max_items=50, description="List of ingredients")
    prep_time: Optional[int] = Field(None, ge=0, le=600, description="Preparation time in minutes")
    cook_time: Optional[int] = Field(None, ge=0, le=1440, description="Cooking time in minutes")
    servings: Optional[int] = Field(None, ge=1, le=20, description="Number of servings")
    difficulty: Optional[str] = Field(None, description="Difficulty level")
    
    @field_validator('instructions')
    @classmethod
    def validate_instructions(cls, v):
        if isinstance(v, list):
            # Convert array to string by joining with newlines
            if not v:
                raise ValueError('Instructions cannot be empty')
            # Clean up each instruction step
            cleaned_steps = []
            for step in v:
                if isinstance(step, str) and step.strip():
                    cleaned_steps.append(step.strip())
            if not cleaned_steps:
                raise ValueError('Instructions cannot be empty')
            return '\n'.join(cleaned_steps)
        elif isinstance(v, str):
            if not v.strip():
                raise ValueError('Instructions cannot be empty')
            if len(v.strip()) < 10:
                raise ValueError('Instructions must be at least 10 characters long')
            return v.strip()
        else:
            raise ValueError('Instructions must be a string or array of strings')
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('Recipe title cannot be empty')
        # Clean up title
        clean_title = re.sub(r'\s+', ' ', v.strip())
        if len(clean_title) < 3:
            raise ValueError('Recipe title must be at least 3 characters long')
        return clean_title
    
    @field_validator('instructions')
    @classmethod
    def validate_instructions(cls, v):
        if isinstance(v, list):
            # Handle list of strings
            if not v:
                raise ValueError('Instructions cannot be empty')
            clean_instructions = []
            for instruction in v:
                if isinstance(instruction, str):
                    clean_instruction = instruction.strip()
                    if clean_instruction:
                        clean_instructions.append(clean_instruction)
            if not clean_instructions:
                raise ValueError('Instructions cannot be empty')
            return clean_instructions
        else:
            # Handle single string
            if not v.strip():
                raise ValueError('Instructions cannot be empty')
            clean_instructions = v.strip()
            if len(clean_instructions) < 10:
                raise ValueError('Instructions must be at least 10 characters long')
            return clean_instructions
    
    @field_validator('difficulty')
    @classmethod
    def validate_difficulty(cls, v):
        if v is None:
            return v
        valid_difficulties = ['Easy', 'Medium', 'Hard', 'Expert']
        if v not in valid_difficulties:
            raise ValueError(f'Difficulty must be one of: {", ".join(valid_difficulties)}')
        return v
    
    @model_validator(mode='after')
    def validate_recipe_times(self):
        if self.prep_time is not None and self.cook_time is not None:
            total_time = self.prep_time + self.cook_time
            if total_time > 1440:  # 24 hours
                raise ValueError('Total cooking time cannot exceed 24 hours')
        return self

class RecipeCreate(RecipeBase):
    pass

class Recipe(RecipeBase):
    id: int
    rating: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class RecipeGenerateRequest(BaseModel):
    ingredients: List[str] = Field(..., min_items=1, max_items=30, description="List of ingredients")
    dietary_preferences: Optional[List[str]] = Field(default=[], max_items=10, description="Dietary preferences")
    cuisine_type: Optional[str] = Field(None, max_length=50, description="Type of cuisine")
    meal_type: Optional[str] = Field(None, max_length=30, description="Type of meal")
    
    @field_validator('ingredients')
    @classmethod
    def validate_ingredients(cls, v):
        if not v:
            raise ValueError('At least one ingredient is required')
        
        cleaned_ingredients = []
        for ingredient in v:
            if not isinstance(ingredient, str):
                raise ValueError('All ingredients must be strings')
            
            clean_ingredient = re.sub(r'\s+', ' ', ingredient.strip())
            if not clean_ingredient:
                raise ValueError('Ingredient cannot be empty')
            
            if len(clean_ingredient) < 2:
                raise ValueError('Ingredient name must be at least 2 characters long')
            
            if len(clean_ingredient) > 100:
                raise ValueError('Ingredient name cannot exceed 100 characters')
            
            if not re.match(r'^[a-zA-Z0-9\s\-\'\.()&,]+$', clean_ingredient):
                raise ValueError(f'Invalid characters in ingredient: {clean_ingredient}')
            
            cleaned_ingredients.append(clean_ingredient)
        
        # Check for duplicates
        if len(cleaned_ingredients) != len(set(cleaned_ingredients)):
            raise ValueError('Duplicate ingredients are not allowed')
        
        return cleaned_ingredients
    
    @field_validator('dietary_preferences')
    @classmethod
    def validate_dietary_preferences(cls, v):
        if v is None:
            return []
        
        valid_diets = [
            'vegetarian', 'vegan', 'gluten-free', 'dairy-free', 'nut-free',
            'low-carb', 'keto', 'paleo', 'mediterranean', 'halal', 'kosher',
            'low-sodium', 'low-fat', 'high-protein', 'diabetic-friendly'
        ]
        
        cleaned_prefs = []
        for pref in v:
            if not isinstance(pref, str):
                raise ValueError('All dietary preferences must be strings')
            
            clean_pref = pref.strip().lower()
            if clean_pref not in valid_diets:
                raise ValueError(f'Invalid dietary preference: {pref}. Valid options: {", ".join(valid_diets)}')
            
            cleaned_prefs.append(clean_pref)
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(cleaned_prefs))
    
    @field_validator('cuisine_type')
    @classmethod
    def validate_cuisine_type(cls, v):
        if v is None:
            return v
        
        valid_cuisines = [
            'italian', 'chinese', 'mexican', 'indian', 'french', 'japanese',
            'thai', 'american', 'mediterranean', 'greek', 'spanish', 'korean',
            'middle-eastern', 'british', 'german', 'vietnamese', 'turkish',
            'moroccan', 'brazilian', 'caribbean', 'african', 'fusion'
        ]
        
        clean_cuisine = v.strip().lower()
        if clean_cuisine not in valid_cuisines:
            raise ValueError(f'Invalid cuisine type: {v}. Valid options: {", ".join(valid_cuisines)}')
        
        return clean_cuisine
    
    @field_validator('meal_type')
    @classmethod
    def validate_meal_type(cls, v):
        if v is None:
            return v
        
        valid_meal_types = [
            'breakfast', 'lunch', 'dinner', 'snack', 'dessert', 'appetizer',
            'main-course', 'side-dish', 'soup', 'salad', 'drink', 'brunch'
        ]
        
        clean_meal = v.strip().lower()
        if clean_meal not in valid_meal_types:
            raise ValueError(f'Invalid meal type: {v}. Valid options: {", ".join(valid_meal_types)}')
        
        return clean_meal

class RecipeGenerateResponse(BaseModel):
    recipes: List[Recipe]

class MealPlanBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description="Meal plan name")
    recipes: Dict[str, List[int]] = Field(..., description="Day to recipe IDs mapping")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Meal plan name cannot be empty')
        
        clean_name = re.sub(r'\s+', ' ', v.strip())
        if len(clean_name) < 3:
            raise ValueError('Meal plan name must be at least 3 characters long')
        
        return clean_name
    
    @field_validator('recipes')
    @classmethod
    def validate_recipes(cls, v):
        if not v:
            raise ValueError('Meal plan must contain at least one day')
        
        valid_days = [
            'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'
        ]
        
        for day, recipe_ids in v.items():
            # Validate day names
            if day.lower() not in valid_days:
                raise ValueError(f'Invalid day: {day}. Must be one of: {", ".join(valid_days)}')
            
            # Validate recipe IDs
            if not isinstance(recipe_ids, list):
                raise ValueError(f'Recipe IDs for {day} must be a list')
            
            if len(recipe_ids) > 10:
                raise ValueError(f'Too many recipes for {day}. Maximum 10 recipes per day')
            
            for recipe_id in recipe_ids:
                if not isinstance(recipe_id, int) or recipe_id <= 0:
                    raise ValueError(f'Invalid recipe ID: {recipe_id}. Must be a positive integer')
        
        return v

class MealPlanCreate(MealPlanBase):
    pass

class MealPlan(MealPlanBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Additional validation schemas for API parameters
class RecipeRatingRequest(BaseModel):
    rating: float = Field(..., ge=1.0, le=5.0, description="Rating between 1.0 and 5.0")
    
    @field_validator('rating')
    @classmethod
    def validate_rating(cls, v):
        if v is None:
            raise ValueError('Rating is required')
        
        # Round to 1 decimal place
        rounded_rating = round(v, 1)
        if rounded_rating < 1.0 or rounded_rating > 5.0:
            raise ValueError('Rating must be between 1.0 and 5.0')
        
        return rounded_rating

class PaginationParams(BaseModel):
    skip: int = Field(default=0, ge=0, le=10000, description="Number of records to skip")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum number of records to return")
    
    @field_validator('skip')
    @classmethod
    def validate_skip(cls, v):
        if v < 0:
            raise ValueError('Skip must be non-negative')
        return v
    
    @field_validator('limit')
    @classmethod
    def validate_limit(cls, v):
        if v < 1:
            raise ValueError('Limit must be at least 1')
        if v > 1000:
            raise ValueError('Limit cannot exceed 1000')
        return v

class RecipeSearchParams(BaseModel):
    q: Optional[str] = Field(None, max_length=200, description="Search query")
    difficulty: Optional[str] = Field(None, description="Filter by difficulty")
    min_rating: Optional[float] = Field(None, ge=1.0, le=5.0, description="Minimum rating")
    max_prep_time: Optional[int] = Field(None, ge=0, le=600, description="Maximum prep time in minutes")
    max_cook_time: Optional[int] = Field(None, ge=0, le=1440, description="Maximum cook time in minutes")
    
    @field_validator('q')
    @classmethod
    def validate_search_query(cls, v):
        if v is None:
            return v
        
        clean_query = v.strip()
        if not clean_query:
            return None
        
        # Remove potentially dangerous characters
        if re.search(r'[<>"\';]', clean_query):
            raise ValueError('Search query contains invalid characters')
        
        return clean_query
    
    @field_validator('difficulty')
    @classmethod
    def validate_difficulty_filter(cls, v):
        if v is None:
            return v
        
        valid_difficulties = ['Easy', 'Medium', 'Hard', 'Expert']
        if v not in valid_difficulties:
            raise ValueError(f'Difficulty must be one of: {", ".join(valid_difficulties)}')
        
        return v

class ErrorResponse(BaseModel):
    detail: str
    error_type: Optional[str] = None
    field_errors: Optional[Dict[str, List[str]]] = None

class SuccessResponse(BaseModel):
    message: str
    data: Optional[Dict[str, Any]] = None

# Pagination response schema
class PaginatedResponse(BaseModel):
    items: List[Recipe]
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number (1-based)")
    pages: int = Field(..., description="Total number of pages")
    per_page: int = Field(..., description="Items per page")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")
    
    @classmethod
    def paginate(cls, items: List[Recipe], total: int, page: int, per_page: int):
        """Helper method to create paginated response"""
        total_pages = (total + per_page - 1) // per_page  # Ceiling division
        
        return cls(
            items=items,
            total=total,
            page=page,
            pages=total_pages,
            per_page=per_page,
            has_next=page < total_pages,
            has_prev=page > 1
        )

class PaginatedMealPlansResponse(BaseModel):
    items: List[MealPlan]
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number (1-based)")
    pages: int = Field(..., description="Total number of pages")
    per_page: int = Field(..., description="Items per page")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")
    
    @classmethod
    def paginate(cls, items: List[MealPlan], total: int, page: int, per_page: int):
        """Helper method to create paginated response"""
        total_pages = (total + per_page - 1) // per_page  # Ceiling division
        
        return cls(
            items=items,
            total=total,
            page=page,
            pages=total_pages,
            per_page=per_page,
            has_next=page < total_pages,
            has_prev=page > 1
        )
