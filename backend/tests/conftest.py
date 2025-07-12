"""
Pytest configuration and shared fixtures for API testing
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db, Base
from app.models import Recipe, MealPlan

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Create test engine with special configuration for SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Override the dependency
    app.dependency_overrides[get_db] = override_get_db

    yield TestingSessionLocal()

    # Clean up
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client for the FastAPI app"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
async def async_client(db_session):
    """Create an async test client for the FastAPI app"""
    async with AsyncClient(app=app, base_url="http://test") as async_test_client:
        yield async_test_client


@pytest.fixture
def sample_recipe_data():
    """Sample recipe data for testing"""
    return {
        "title": "Test Chicken Pasta",
        "description": "A delicious test recipe with chicken and pasta",
        "instructions": "1. Cook pasta according to package directions. 2. Season chicken with salt and pepper. 3. Cook chicken in a skillet until done.",
        "ingredients": [
            {
                "name": "chicken breast",
                "amount": "2",
                "unit": "pieces",
                "notes": "boneless",
            },
            {
                "name": "pasta",
                "amount": "200",
                "unit": "g",
                "notes": "penne or fusilli",
            },
            {"name": "olive oil", "amount": "2", "unit": "tbsp", "notes": None},
            {"name": "salt", "amount": "1", "unit": "tsp", "notes": "to taste"},
        ],
        "prep_time": 15,
        "cook_time": 25,
        "servings": 4,
        "difficulty": "Easy",
    }


@pytest.fixture
def sample_vegetarian_recipe_data():
    """Sample vegetarian recipe data for testing"""
    return {
        "title": "Vegetarian Pasta Primavera",
        "description": "Fresh vegetables with pasta in a light sauce",
        "instructions": "1. Cook pasta. 2. Sauté vegetables. 3. Combine with herbs.",
        "ingredients": [
            {"name": "pasta", "amount": "200", "unit": "g", "notes": "any shape"},
            {
                "name": "bell peppers",
                "amount": "2",
                "unit": "pieces",
                "notes": "mixed colors",
            },
            {"name": "zucchini", "amount": "1", "unit": "medium", "notes": "sliced"},
            {
                "name": "cherry tomatoes",
                "amount": "200",
                "unit": "g",
                "notes": "halved",
            },
        ],
        "prep_time": 10,
        "cook_time": 20,
        "servings": 3,
        "difficulty": "Medium",
    }


@pytest.fixture
def sample_meal_plan_data():
    """Sample meal plan data for testing"""
    return {
        "name": "Test Weekly Plan",
        "recipes": {
            "Monday": [],
            "Tuesday": [],
            "Wednesday": [],
            "Thursday": [],
            "Friday": [],
            "Saturday": [],
            "Sunday": [],
        },
    }


@pytest.fixture
def multiple_recipes_data():
    """Multiple recipes for pagination testing"""
    recipes = []
    for i in range(15):
        recipes.append(
            {
                "title": f"Test Recipe {i+1}",
                "description": f"Description for recipe {i+1}",
                "instructions": f"1. Step 1 for recipe {i+1}. 2. Step 2 for recipe {i+1}.",
                "ingredients": [
                    {
                        "name": f"ingredient_{i+1}_1",
                        "amount": str(i + 1),
                        "unit": "cup",
                        "notes": None,
                    },
                    {
                        "name": f"ingredient_{i+1}_2",
                        "amount": "2",
                        "unit": "tbsp",
                        "notes": None,
                    },
                ],
                "prep_time": 10 + i,
                "cook_time": 20 + i,
                "servings": (i % 4) + 2,
                "difficulty": ["Easy", "Medium", "Hard"][i % 3],
            }
        )
    return recipes


@pytest.fixture
def created_recipe(client, sample_recipe_data):
    """Create a recipe and return its data"""
    response = client.post("/api/recipes", json=sample_recipe_data)
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def created_multiple_recipes(client, multiple_recipes_data):
    """Create multiple recipes for testing pagination"""
    created_recipes = []
    for recipe_data in multiple_recipes_data:
        response = client.post("/api/recipes", json=recipe_data)
        assert response.status_code == 200
        created_recipes.append(response.json())
    return created_recipes
