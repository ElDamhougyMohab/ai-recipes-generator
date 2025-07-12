"""
Tests for validation schemas
"""
import pytest
from pydantic import ValidationError

from app.schemas import (
    RecipeCreate, 
    IngredientSchema, 
    MealPlanCreate,
    PaginatedResponse
)


class TestIngredientSchema:
    """Test cases for ingredient validation"""
    
    def test_ingredient_valid_data(self):
        """Test valid ingredient data"""
        ingredient = IngredientSchema(
            name="chicken breast",
            amount="2",
            unit="pieces",
            notes="boneless"
        )
        
        assert ingredient.name == "chicken breast"
        assert ingredient.amount == 2.0  # Amount is converted to float
        assert ingredient.unit == "pieces"
        assert ingredient.notes == "boneless"
    
    def test_ingredient_required_fields(self):
        """Test ingredient with only required fields"""
        ingredient = IngredientSchema(name="salt")
        
        assert ingredient.name == "salt"
        assert ingredient.amount is None
        assert ingredient.unit is None
        assert ingredient.notes is None
    
    def test_ingredient_empty_name(self):
        """Test ingredient with empty name"""
        with pytest.raises(ValidationError) as exc_info:
            IngredientSchema(name="")
        
        assert "String should have at least 1 character" in str(exc_info.value)
    
    def test_ingredient_whitespace_name(self):
        """Test ingredient with whitespace-only name"""
        with pytest.raises(ValidationError) as exc_info:
            IngredientSchema(name="   ")
        
        assert "Ingredient name cannot be empty" in str(exc_info.value)
    
    def test_ingredient_name_cleaning(self):
        """Test ingredient name cleaning"""
        ingredient = IngredientSchema(name="  chicken   breast  ")
        
        assert ingredient.name == "chicken breast"
    
    def test_ingredient_invalid_characters(self):
        """Test ingredient with invalid characters"""
        with pytest.raises(ValidationError) as exc_info:
            IngredientSchema(name="ingredient<script>")
        
        assert "invalid characters" in str(exc_info.value)
    
    def test_ingredient_unicode_characters(self):
        """Test ingredient with unicode characters"""
        ingredient = IngredientSchema(name="jalapeño peppers")
        
        assert ingredient.name == "jalapeño peppers"
    
    def test_ingredient_amount_validation(self):
        """Test ingredient amount validation"""
        # Test numeric amounts
        ingredient1 = IngredientSchema(name="flour", amount=2.5)
        assert ingredient1.amount == 2.5
        
        # Test string amounts
        ingredient2 = IngredientSchema(name="salt", amount="to taste")
        assert ingredient2.amount == "to taste"
        
        # Test fraction amounts
        ingredient3 = IngredientSchema(name="butter", amount="1/2")
        assert ingredient3.amount == 0.5
    
    def test_ingredient_unit_validation(self):
        """Test ingredient unit validation"""
        ingredient = IngredientSchema(
            name="flour",
            amount="2",
            unit="  cups  "
        )
        
        assert ingredient.unit == "cups"


class TestRecipeSchema:
    """Test cases for recipe validation"""
    
    def test_recipe_valid_data(self):
        """Test valid recipe data"""
        recipe_data = {
            "title": "Test Recipe",
            "description": "A test recipe",
            "instructions": "1. Step one. 2. Step two.",
            "ingredients": [
                {"name": "ingredient1", "amount": "1", "unit": "cup"},
                {"name": "ingredient2", "amount": "2", "unit": "tbsp"}
            ],
            "prep_time": 15,
            "cook_time": 30,
            "servings": 4,
            "difficulty": "Easy"
        }
        
        recipe = RecipeCreate(**recipe_data)
        
        assert recipe.title == "Test Recipe"
        assert recipe.description == "A test recipe"
        assert recipe.prep_time == 15
        assert recipe.cook_time == 30
        assert recipe.servings == 4
        assert recipe.difficulty == "Easy"
        assert len(recipe.ingredients) == 2
    
    def test_recipe_required_fields(self):
        """Test recipe with only required fields"""
        recipe_data = {
            "title": "Minimal Recipe",
            "instructions": "Cook the food.",
            "ingredients": [{"name": "food", "amount": "1", "unit": "piece"}]
        }
        
        recipe = RecipeCreate(**recipe_data)
        
        assert recipe.title == "Minimal Recipe"
        assert recipe.description is None
        assert recipe.prep_time is None
        assert recipe.cook_time is None
        assert recipe.servings is None
        assert recipe.difficulty is None
    
    def test_recipe_missing_title(self):
        """Test recipe without title"""
        recipe_data = {
            "instructions": "Cook the food.",
            "ingredients": [{"name": "food", "amount": "1", "unit": "piece"}]
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RecipeCreate(**recipe_data)
        
        assert "title" in str(exc_info.value)
    
    def test_recipe_empty_title(self):
        """Test recipe with empty title"""
        recipe_data = {
            "title": "",
            "instructions": "Cook the food.",
            "ingredients": [{"name": "food", "amount": "1", "unit": "piece"}]
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RecipeCreate(**recipe_data)
        
        assert "String should have at least 3 characters" in str(exc_info.value)
    
    def test_recipe_short_title(self):
        """Test recipe with too short title"""
        recipe_data = {
            "title": "Ab",  # Less than 3 characters
            "instructions": "Cook the food.",
            "ingredients": [{"name": "food", "amount": "1", "unit": "piece"}]
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RecipeCreate(**recipe_data)
        
        assert "at least 3 characters" in str(exc_info.value)
    
    def test_recipe_long_title(self):
        """Test recipe with maximum length title"""
        recipe_data = {
            "title": "A" * 200,  # Maximum allowed length
            "instructions": "Cook the food.",
            "ingredients": [{"name": "food", "amount": "1", "unit": "piece"}]
        }
        
        recipe = RecipeCreate(**recipe_data)
        assert len(recipe.title) == 200
    
    def test_recipe_too_long_title(self):
        """Test recipe with too long title"""
        recipe_data = {
            "title": "A" * 201,  # Over maximum length
            "instructions": "Cook the food.",
            "ingredients": [{"name": "food", "amount": "1", "unit": "piece"}]
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RecipeCreate(**recipe_data)
        
        assert "200" in str(exc_info.value)
    
    def test_recipe_empty_ingredients(self):
        """Test recipe with empty ingredients"""
        recipe_data = {
            "title": "Test Recipe",
            "instructions": "Cook the food.",
            "ingredients": []
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RecipeCreate(**recipe_data)
        
        assert "at least 1 item" in str(exc_info.value)
    
    def test_recipe_too_many_ingredients(self):
        """Test recipe with too many ingredients"""
        recipe_data = {
            "title": "Test Recipe",
            "instructions": "Cook the food.",
            "ingredients": [
                {"name": f"ingredient_{i}", "amount": "1", "unit": "cup"}
                for i in range(51)  # Over maximum of 50
            ]
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RecipeCreate(**recipe_data)
        
        assert "50" in str(exc_info.value)
    
    def test_recipe_invalid_difficulty(self):
        """Test recipe with invalid difficulty"""
        recipe_data = {
            "title": "Test Recipe",
            "instructions": "Cook the food.",
            "ingredients": [{"name": "food", "amount": "1", "unit": "piece"}],
            "difficulty": "Invalid"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RecipeCreate(**recipe_data)
        
        assert "Difficulty must be one of" in str(exc_info.value)
    
    def test_recipe_valid_difficulties(self):
        """Test recipe with all valid difficulties"""
        valid_difficulties = ["Easy", "Medium", "Hard", "Expert"]
        
        for difficulty in valid_difficulties:
            recipe_data = {
                "title": "Test Recipe",
                "instructions": "Cook the food.",
                "ingredients": [{"name": "food", "amount": "1", "unit": "piece"}],
                "difficulty": difficulty
            }
            
            recipe = RecipeCreate(**recipe_data)
            assert recipe.difficulty == difficulty
    
    def test_recipe_time_validation(self):
        """Test recipe time validation"""
        # Test negative prep time
        recipe_data = {
            "title": "Test Recipe",
            "instructions": "Cook the food.",
            "ingredients": [{"name": "food", "amount": "1", "unit": "piece"}],
            "prep_time": -1
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RecipeCreate(**recipe_data)
        
        assert "greater than or equal to 0" in str(exc_info.value)
        
        # Test too long cook time
        recipe_data_long = {
            "title": "Test Recipe",
            "instructions": "Cook the food.",
            "ingredients": [{"name": "food", "amount": "1", "unit": "piece"}],
            "cook_time": 1441  # Over 24 hours
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RecipeCreate(**recipe_data_long)
        
        assert "1440" in str(exc_info.value)
    
    def test_recipe_servings_validation(self):
        """Test recipe servings validation"""
        # Test zero servings
        recipe_data = {
            "title": "Test Recipe",
            "instructions": "Cook the food.",
            "ingredients": [{"name": "food", "amount": "1", "unit": "piece"}],
            "servings": 0
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RecipeCreate(**recipe_data)
        
        assert "greater than or equal to 1" in str(exc_info.value)
        
        # Test too many servings
        recipe_data_many = {
            "title": "Test Recipe",
            "instructions": "Cook the food.",
            "ingredients": [{"name": "food", "amount": "1", "unit": "piece"}],
            "servings": 21  # Over maximum of 20
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RecipeCreate(**recipe_data_many)
        
        assert "20" in str(exc_info.value)
    
    def test_recipe_total_time_validation(self):
        """Test recipe total time validation"""
        recipe_data = {
            "title": "Test Recipe",
            "instructions": "Cook the food.",
            "ingredients": [{"name": "food", "amount": "1", "unit": "piece"}],
            "prep_time": 800,  # 13+ hours
            "cook_time": 700   # 11+ hours - total over 24 hours
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RecipeCreate(**recipe_data)
        
        assert "24 hours" in str(exc_info.value)
    
    def test_recipe_instructions_validation(self):
        """Test recipe instructions validation"""
        # Test empty instructions
        recipe_data = {
            "title": "Test Recipe",
            "instructions": "",
            "ingredients": [{"name": "food", "amount": "1", "unit": "piece"}]
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RecipeCreate(**recipe_data)
        
        assert "Instructions cannot be empty" in str(exc_info.value)
        
        # Test too short instructions
        recipe_data_short = {
            "title": "Test Recipe",
            "instructions": "Cook.",  # Less than 10 characters
            "ingredients": [{"name": "food", "amount": "1", "unit": "piece"}]
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RecipeCreate(**recipe_data_short)
        
        assert "at least 10 characters" in str(exc_info.value)


class TestMealPlanSchema:
    """Test cases for meal plan validation"""
    
    def test_meal_plan_valid_data(self):
        """Test valid meal plan data"""
        meal_plan_data = {
            "name": "Test Plan",
            "recipes": {
                "Monday": [1, 2],
                "Tuesday": [3],
                "Wednesday": [],
                "Thursday": [1, 3],
                "Friday": [],
                "Saturday": [2],
                "Sunday": [1, 2, 3]
            }
        }
        
        meal_plan = MealPlanCreate(**meal_plan_data)
        
        assert meal_plan.name == "Test Plan"
        assert len(meal_plan.recipes) == 7
        assert meal_plan.recipes["Monday"] == [1, 2]
        assert meal_plan.recipes["Wednesday"] == []
    
    def test_meal_plan_missing_name(self):
        """Test meal plan without name"""
        meal_plan_data = {
            "recipes": {
                "Monday": [],
                "Tuesday": [],
                "Wednesday": [],
                "Thursday": [],
                "Friday": [],
                "Saturday": [],
                "Sunday": []
            }
        }
        
        with pytest.raises(ValidationError) as exc_info:
            MealPlanCreate(**meal_plan_data)
        
        assert "name" in str(exc_info.value)
    
    def test_meal_plan_empty_name(self):
        """Test meal plan with empty name"""
        meal_plan_data = {
            "name": "",
            "recipes": {
                "Monday": [],
                "Tuesday": [],
                "Wednesday": [],
                "Thursday": [],
                "Friday": [],
                "Saturday": [],
                "Sunday": []
            }
        }
        
        with pytest.raises(ValidationError) as exc_info:
            MealPlanCreate(**meal_plan_data)
        
        assert "at least 1 character" in str(exc_info.value)
    
    def test_meal_plan_invalid_day_names(self):
        """Test meal plan with invalid day names"""
        meal_plan_data = {
            "name": "Test Plan",
            "recipes": {
                "InvalidDay": [],
                "Tuesday": [],
                "Wednesday": [],
                "Thursday": [],
                "Friday": [],
                "Saturday": [],
                "Sunday": []
            }
        }
        
        with pytest.raises(ValidationError) as exc_info:
            MealPlanCreate(**meal_plan_data)
        
        assert "Invalid day name" in str(exc_info.value)
    
    def test_meal_plan_missing_days(self):
        """Test meal plan with missing days"""
        meal_plan_data = {
            "name": "Test Plan",
            "recipes": {
                "Monday": [],
                "Tuesday": [],
                "Wednesday": [],
                "Thursday": [],
                "Friday": [],
                "Saturday": []
                # Missing Sunday
            }
        }
        
        with pytest.raises(ValidationError) as exc_info:
            MealPlanCreate(**meal_plan_data)
        
        assert "All 7 days" in str(exc_info.value)
    
    def test_meal_plan_recipe_id_validation(self):
        """Test meal plan recipe ID validation"""
        # Test negative recipe ID
        meal_plan_data = {
            "name": "Test Plan",
            "recipes": {
                "Monday": [-1],
                "Tuesday": [],
                "Wednesday": [],
                "Thursday": [],
                "Friday": [],
                "Saturday": [],
                "Sunday": []
            }
        }
        
        with pytest.raises(ValidationError) as exc_info:
            MealPlanCreate(**meal_plan_data)
        
        assert "positive integer" in str(exc_info.value)
        
        # Test zero recipe ID
        meal_plan_data_zero = {
            "name": "Test Plan",
            "recipes": {
                "Monday": [0],
                "Tuesday": [],
                "Wednesday": [],
                "Thursday": [],
                "Friday": [],
                "Saturday": [],
                "Sunday": []
            }
        }
        
        with pytest.raises(ValidationError) as exc_info:
            MealPlanCreate(**meal_plan_data_zero)
        
        assert "positive integer" in str(exc_info.value)
