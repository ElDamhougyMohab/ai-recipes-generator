import google.generativeai as genai
import aiohttp
import asyncio
import os
import json
import re
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class GeminiAPIError(Exception):
    """Custom exception for Gemini API errors"""
    pass

class GeminiTimeoutError(Exception):
    """Custom exception for Gemini API timeouts"""
    pass


class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")

        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        
        # Configure the synchronous client as fallback
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Thread pool for sync operations
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        # Semaphore to limit concurrent requests
        self.semaphore = asyncio.Semaphore(3)
        
        # Session will be created per request
        self.session = None

        # Define dietary restriction mappings
        self.dietary_restrictions = {
            "vegetarian": {
                "forbidden_ingredients": [
                    "chicken",
                    "beef",
                    "pork",
                    "lamb",
                    "turkey",
                    "duck",
                    "fish",
                    "salmon",
                    "tuna",
                    "shrimp",
                    "crab",
                    "lobster",
                    "meat",
                    "bacon",
                    "ham",
                    "sausage",
                    "pepperoni",
                ],
                "allowed_proteins": [
                    "tofu",
                    "tempeh",
                    "beans",
                    "lentils",
                    "chickpeas",
                    "quinoa",
                    "nuts",
                    "seeds",
                    "eggs",
                    "dairy",
                ],
            },
            "vegan": {
                "forbidden_ingredients": [
                    "chicken",
                    "beef",
                    "pork",
                    "lamb",
                    "turkey",
                    "duck",
                    "fish",
                    "salmon",
                    "tuna",
                    "shrimp",
                    "crab",
                    "lobster",
                    "meat",
                    "bacon",
                    "ham",
                    "sausage",
                    "pepperoni",
                    "eggs",
                    "milk",
                    "cheese",
                    "butter",
                    "yogurt",
                    "cream",
                ],
                "allowed_proteins": [
                    "tofu",
                    "tempeh",
                    "beans",
                    "lentils",
                    "chickpeas",
                    "quinoa",
                    "nuts",
                    "seeds",
                    "nutritional yeast",
                ],
            },
            "gluten-free": {
                "forbidden_ingredients": [
                    "wheat",
                    "barley",
                    "rye",
                    "flour",
                    "bread",
                    "pasta",
                    "noodles",
                    "soy sauce",
                ],
                "allowed_alternatives": [
                    "rice",
                    "quinoa",
                    "gluten-free flour",
                    "corn",
                    "potatoes",
                ],
            },
            "dairy-free": {
                "forbidden_ingredients": [
                    "milk",
                    "cheese",
                    "butter",
                    "yogurt",
                    "cream",
                    "ice cream",
                ],
                "allowed_alternatives": [
                    "almond milk",
                    "coconut milk",
                    "vegan cheese",
                    "coconut oil",
                ],
            },
        }

    def _filter_ingredients_by_diet(
        self, ingredients: List[str], dietary_preferences: Optional[List[str]] = None
    ) -> tuple[List[str], List[str]]:
        """Filter ingredients based on dietary restrictions and return allowed ingredients and suggestions for replacements"""
        if not dietary_preferences:
            return ingredients, []

        allowed_ingredients = []
        forbidden_ingredients = []
        suggestions = []

        for ingredient in ingredients:
            ingredient_lower = ingredient.lower()
            is_forbidden = False

            for diet in dietary_preferences:
                diet_lower = diet.lower()
                if diet_lower in self.dietary_restrictions:
                    forbidden_list = self.dietary_restrictions[diet_lower].get(
                        "forbidden_ingredients", []
                    )
                    if any(
                        forbidden_item in ingredient_lower
                        for forbidden_item in forbidden_list
                    ):
                        is_forbidden = True
                        forbidden_ingredients.append(ingredient)

                        # Add suggestions for replacements
                        if diet_lower in ["vegetarian", "vegan"] and any(
                            meat in ingredient_lower
                            for meat in ["chicken", "beef", "pork", "meat"]
                        ):
                            suggestions.extend(
                                self.dietary_restrictions[diet_lower][
                                    "allowed_proteins"
                                ]
                            )
                        break

            if not is_forbidden:
                allowed_ingredients.append(ingredient)

        return allowed_ingredients, list(set(suggestions))

    async def generate_recipes(
        self,
        ingredients: List[str],
        dietary_preferences: Optional[List[str]] = None,
        cuisine_type: Optional[str] = None,
        meal_type: Optional[str] = None,
        timeout: int = 30,
    ) -> List[Dict[str, Any]]:
        """
        Generate recipes asynchronously using Gemini API
        
        Args:
            ingredients: List of available ingredients
            dietary_preferences: Dietary restrictions to apply
            cuisine_type: Preferred cuisine style
            meal_type: Type of meal (breakfast, lunch, dinner, snack)
            timeout: Request timeout in seconds
            
        Returns:
            List of generated recipe dictionaries
        """
        # Apply semaphore to limit concurrent requests
        async with self.semaphore:
            try:
                logger.info(f"🚀 Starting async recipe generation with {len(ingredients)} ingredients")
                
                # Filter ingredients based on dietary restrictions
                allowed_ingredients, protein_suggestions = self._filter_ingredients_by_diet(
                    ingredients, dietary_preferences
                )

                # Build the prompt
                prompt = self._build_prompt(
                    allowed_ingredients,
                    dietary_preferences,
                    cuisine_type,
                    meal_type,
                    protein_suggestions,
                )

                # Try async HTTP call first, fall back to sync if needed
                recipes_data = await self._call_gemini_async(prompt, timeout)
                
                # Validate recipes against dietary restrictions
                validated_recipes = self._validate_recipes_against_diet(
                    recipes_data, dietary_preferences
                )

                logger.info(f"✅ Successfully generated {len(validated_recipes)} recipes")
                return validated_recipes
                
            except asyncio.TimeoutError:
                logger.error(f"⏰ Gemini API timeout after {timeout} seconds")
                return await self._get_fallback_recipes_async(allowed_ingredients, dietary_preferences)
                
            except Exception as e:
                logger.error(f"❌ Gemini API error: {str(e)}")
                return await self._get_fallback_recipes_async(allowed_ingredients, dietary_preferences)
    
    async def _call_gemini_async(self, prompt: str, timeout: int = 30) -> List[Dict[str, Any]]:
        """
        Make async HTTP call to Gemini API
        """
        try:
            # Prepare the request payload
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 2048,
                    "topP": 0.8,
                    "topK": 40
                }
            }
            
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key
            }
            
            # Create session for this request
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                logger.info("📡 Making async HTTP request to Gemini API")
                
                async with session.post(self.base_url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info("📡 Received successful response from Gemini API")
                        return await self._parse_response_async(data)
                    else:
                        error_text = await response.text()
                        logger.error(f"📡 Gemini API HTTP error: {response.status} - {error_text}")
                        raise GeminiAPIError(f"API returned {response.status}: {error_text}")
                        
        except asyncio.TimeoutError:
            logger.error("📡 Async HTTP request timeout")
            # Fallback to sync method
            return await self._call_gemini_sync_fallback(prompt)
            
        except Exception as e:
            logger.error(f"📡 Async HTTP request failed: {str(e)}")
            # Fallback to sync method
            return await self._call_gemini_sync_fallback(prompt)
    
    async def _call_gemini_sync_fallback(self, prompt: str) -> List[Dict[str, Any]]:
        """
        Fallback to sync Gemini API call in thread pool
        """
        try:
            logger.info("📡 Falling back to sync Gemini API call")
            
            loop = asyncio.get_event_loop()
            
            # Run sync API call in thread pool
            response = await loop.run_in_executor(
                self.executor,
                self.model.generate_content,
                prompt
            )
            
            logger.info("📡 Sync fallback successful")
            return self._parse_response(response.text)
            
        except Exception as e:
            logger.error(f"📡 Sync fallback failed: {str(e)}")
            raise GeminiAPIError(f"Both async and sync calls failed: {str(e)}")
    
    async def _parse_response_async(self, data: Dict) -> List[Dict[str, Any]]:
        """
        Parse async HTTP response from Gemini API
        """
        try:
            content = data['candidates'][0]['content']['parts'][0]['text']
            
            # Use the existing sync parsing method
            return self._parse_response(content)
            
        except Exception as e:
            logger.error(f"📡 Error parsing async response: {str(e)}")
            raise GeminiAPIError(f"Failed to parse response: {str(e)}")
    
    async def _get_fallback_recipes_async(
        self, 
        ingredients: List[str], 
        dietary_preferences: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get fallback recipes asynchronously
        """
        logger.info("🔄 Generating fallback recipes")
        
        # Use existing sync method but wrap in async
        return self._get_fallback_recipes(ingredients, dietary_preferences)

    def _build_prompt(
        self,
        ingredients: List[str],
        dietary_preferences: Optional[List[str]] = None,
        cuisine_type: Optional[str] = None,
        meal_type: Optional[str] = None,
        protein_suggestions: Optional[List[str]] = None,
    ) -> str:
        ingredients_str = ", ".join(ingredients)

        prompt = f"""
You are a professional chef and recipe developer. Create 2-3 detailed, restaurant-quality recipes using these ingredients: {ingredients_str}

EXAMPLES OF THE QUALITY I EXPECT:

Example Recipe Format:
**Chicken & Spinach Tomato Pasta with Roasted Potatoes** (serves 2-3)

**Ingredients:**
- Pasta – 200g (penne, fusilli, or your choice)
- Chicken breast – 1 large (≈250g), cut into 2cm cubes  
- Tomatoes – 3 medium (≈350g total), diced
- Potatoes – 2 medium (≈300g total), scrubbed and cut into 1cm cubes
- Spinach – 100g fresh, roughly chopped
- Olive oil – 3 Tbsp
- Salt & black pepper – to taste
- Optional: 1 tsp dried oregano, pinch of chili flakes

**Instructions:**
1. **Roast the potatoes:** Preheat oven to 200°C (390°F). Toss potato cubes with 1 Tbsp olive oil, ½ tsp salt and pepper. Spread on baking sheet and roast 25-30 minutes until golden-brown and crisp.

2. **Cook the pasta:** Bring large pot of water to boil. Salt generously (≈1 Tbsp). Add pasta and cook until al dente (8-10 min). Reserve ½ cup pasta water, then drain.

3. **Sear the chicken:** Heat large skillet over medium-high heat. Add 1 Tbsp olive oil, then cubed chicken. Season and sear until golden all over, 6-8 minutes. Transfer to plate.

4. **Build the sauce:** In same skillet, add diced tomatoes, salt, oregano and chili flakes. Cook until tomatoes soften, 4-5 minutes. Add spinach and cook until wilted, 1-2 minutes.

5. **Combine & finish:** Return chicken to skillet. Add drained pasta and reserved pasta water. Toss 1-2 minutes until sauce coats noodles. Adjust seasoning.

6. **Serve:** Divide pasta between plates. Add roasted potatoes alongside. Drizzle with extra olive oil if desired.

**Total time:** ≈40 minutes

YOUR TASK:
Create recipes with this level of detail, professional techniques, and clear step-by-step instructions.

REQUIREMENTS:
- Use ALL the provided ingredients creatively
- Include specific quantities and measurements  
- Add complementary ingredients to make complete, balanced meals
- Provide professional cooking techniques and tips
- Include cooking times and temperatures
- Make instructions clear and detailed
- Create recipes that are practical and achievable
"""

        if protein_suggestions:
            prompt += f"\n- You may include these additional proteins: {', '.join(protein_suggestions)}"

        if dietary_preferences:
            dietary_str = ", ".join(dietary_preferences)
            prompt += f"""
        
**DIETARY RESTRICTIONS - STRICTLY ENFORCE:**
- Follow these dietary preferences: {dietary_str}
- If vegetarian: NO meat, poultry, fish, or seafood
- If vegan: NO animal products (meat, dairy, eggs, honey, etc.)
- If gluten-free: NO wheat, barley, rye, or gluten-containing ingredients
- If dairy-free: NO milk, cheese, butter, yogurt, or dairy products
"""

        if cuisine_type and cuisine_type.lower() != "any":
            prompt += f"\n- Style: {cuisine_type} cuisine with authentic flavors and techniques"

        if meal_type and meal_type.lower() != "any":
            prompt += f"\n- Meal type: {meal_type}"

        prompt += """

**JSON FORMAT:**
Return your response as a JSON array with this exact structure:

[
  {
    "title": "Professional Recipe Name",
    "description": "Detailed description highlighting key flavors and techniques",
    "instructions": "1. First step with specific technique and timing. 2. Second step with temperature and visual cues. 3. Continue with detailed professional instructions...",
    "ingredients": [
      {"name": "main ingredient", "amount": "200", "unit": "g"},
      {"name": "secondary ingredient", "amount": "3", "unit": "medium"},
      {"name": "seasoning", "amount": "1", "unit": "tsp"}
    ],
    "prep_time": 15,
    "cook_time": 25,
    "servings": 2,
    "difficulty": "Easy"
  }
]

**CRITICAL:**
- Make each recipe unique and creative
- Use professional cooking terminology
- Include specific weights/measurements where appropriate
- Provide detailed, step-by-step instructions like a professional cookbook
- Ensure perfect JSON formatting
- Focus on flavor development and proper technique
"""

        return prompt

    def _validate_recipes_against_diet(
        self,
        recipes: List[Dict[str, Any]],
        dietary_preferences: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Validate recipes against dietary restrictions and remove non-compliant ingredients"""
        if not dietary_preferences:
            return recipes

        validated_recipes = []

        for recipe in recipes:
            is_valid = True
            cleaned_ingredients = []

            for ingredient in recipe.get("ingredients", []):
                ingredient_name = ingredient.get("name", "").lower()
                ingredient_valid = True

                for diet in dietary_preferences:
                    diet_lower = diet.lower()
                    if diet_lower in self.dietary_restrictions:
                        forbidden_list = self.dietary_restrictions[diet_lower].get(
                            "forbidden_ingredients", []
                        )
                        if any(
                            forbidden_item in ingredient_name
                            for forbidden_item in forbidden_list
                        ):
                            ingredient_valid = False
                            break

                if ingredient_valid:
                    cleaned_ingredients.append(ingredient)

            if cleaned_ingredients:  # Only include recipe if it has valid ingredients
                recipe["ingredients"] = cleaned_ingredients
                validated_recipes.append(recipe)

        return validated_recipes

    def _parse_response(self, response_text: str) -> List[Dict[str, Any]]:
        try:
            # Extract JSON from response
            json_match = re.search(r"\[.*\]", response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                recipes = json.loads(json_str)
                return recipes
            else:
                raise ValueError("No valid JSON found in response")
        except (json.JSONDecodeError, ValueError) as e:
            # If parsing fails, create structured data from text
            return self._parse_text_response(response_text)

    def _parse_text_response(self, text: str) -> List[Dict[str, Any]]:
        # Fallback parser for non-JSON responses
        recipes = []

        # Split by recipe sections (assuming numbered recipes)
        recipe_sections = re.split(r"\n(?=\d+\.|\*\*Recipe)", text)

        for section in recipe_sections:
            if len(section.strip()) < 50:  # Skip short sections
                continue

            recipe = {
                "title": "Generated Recipe",
                "description": "AI generated recipe",
                "instructions": section.strip(),
                "ingredients": [
                    {"name": "Various ingredients", "amount": "As needed", "unit": ""}
                ],
                "prep_time": 20,
                "cook_time": 30,
                "servings": 4,
                "difficulty": "Medium",
            }

            # Try to extract title
            title_match = re.search(
                r"(?:Recipe \d+:|^\d+\.|^\*\*)(.*?)(?:\n|\*\*)", section
            )
            if title_match:
                recipe["title"] = title_match.group(1).strip()

            recipes.append(recipe)

        return recipes[:3]  # Limit to 3 recipes

    def _get_fallback_recipes(
        self, ingredients: List[str], dietary_preferences: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        # Filter ingredients based on dietary restrictions
        allowed_ingredients, _ = self._filter_ingredients_by_diet(
            ingredients, dietary_preferences
        )

        if not allowed_ingredients:
            # If no ingredients are allowed, create a basic recipe with alternatives
            if dietary_preferences and "vegetarian" in [
                d.lower() for d in dietary_preferences
            ]:
                allowed_ingredients = ["tofu", "vegetables", "rice"]
            elif dietary_preferences and "vegan" in [
                d.lower() for d in dietary_preferences
            ]:
                allowed_ingredients = ["tofu", "vegetables", "quinoa"]
            else:
                allowed_ingredients = ["vegetables", "rice"]

        # Create dietary-compliant fallback recipes
        fallback_recipes = []

        if dietary_preferences and "vegetarian" in [
            d.lower() for d in dietary_preferences
        ]:
            fallback_recipes.append(
                {
                    "title": f"Vegetarian {' & '.join(allowed_ingredients[:2])} Stir-Fry",
                    "description": "A delicious vegetarian dish using your ingredients",
                    "instructions": f"1. Heat oil in a pan. 2. Add {', '.join(allowed_ingredients)} and stir-fry for 8-10 minutes. 3. Season with herbs and spices. 4. Serve hot with rice or quinoa.",
                    "ingredients": [
                        {"name": ing, "amount": "1 cup", "unit": "cup"}
                        for ing in allowed_ingredients
                    ]
                    + [{"name": "olive oil", "amount": "2 tbsp", "unit": "tbsp"}],
                    "prep_time": 10,
                    "cook_time": 15,
                    "servings": 2,
                    "difficulty": "Easy",
                }
            )
        elif dietary_preferences and "vegan" in [
            d.lower() for d in dietary_preferences
        ]:
            fallback_recipes.append(
                {
                    "title": f"Vegan {' & '.join(allowed_ingredients[:2])} Bowl",
                    "description": "A nutritious vegan recipe using your ingredients",
                    "instructions": f"1. Prepare {', '.join(allowed_ingredients)} by washing and chopping. 2. Cook quinoa according to package directions. 3. Sauté vegetables in olive oil. 4. Combine all ingredients and serve.",
                    "ingredients": [
                        {"name": ing, "amount": "1 cup", "unit": "cup"}
                        for ing in allowed_ingredients
                    ]
                    + [
                        {"name": "quinoa", "amount": "1 cup", "unit": "cup"},
                        {"name": "olive oil", "amount": "2 tbsp", "unit": "tbsp"},
                    ],
                    "prep_time": 15,
                    "cook_time": 20,
                    "servings": 2,
                    "difficulty": "Easy",
                }
            )
        else:
            fallback_recipes.append(
                {
                    "title": f"Simple {' & '.join(allowed_ingredients[:2])} Dish",
                    "description": "A quick and easy recipe using your ingredients",
                    "instructions": f"1. Prepare your {allowed_ingredients[0]} by washing and chopping. 2. Heat oil in a pan. 3. Add {allowed_ingredients[0]} and cook for 5 minutes. 4. Add remaining ingredients and season to taste. 5. Cook until tender and serve hot.",
                    "ingredients": [
                        {"name": ing, "amount": "1 cup", "unit": "cup"}
                        for ing in allowed_ingredients
                    ],
                    "prep_time": 10,
                    "cook_time": 20,
                    "servings": 2,
                    "difficulty": "Easy",
                }
            )

        return fallback_recipes

    async def generate_multiple_recipes(
        self, 
        requests: List[Dict[str, Any]]
    ) -> List[List[Dict[str, Any]]]:
        """
        Generate multiple recipe sets concurrently
        
        Args:
            requests: List of recipe generation requests
            
        Returns:
            List of recipe lists for each request
        """
        try:
            logger.info(f"🚀 Starting batch generation for {len(requests)} requests")
            
            # Create tasks for concurrent execution
            tasks = []
            for i, request in enumerate(requests):
                task = self.generate_recipes(
                    ingredients=request.get('ingredients', []),
                    dietary_preferences=request.get('dietary_preferences'),
                    cuisine_type=request.get('cuisine_type'),
                    meal_type=request.get('meal_type')
                )
                tasks.append(task)
            
            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and handle exceptions
            successful_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"❌ Batch request {i} failed: {result}")
                    # Generate fallback for failed request
                    fallback = await self._get_fallback_recipes_async(
                        requests[i].get('ingredients', []), 
                        requests[i].get('dietary_preferences')
                    )
                    successful_results.append(fallback)
                else:
                    successful_results.append(result)
            
            logger.info(f"✅ Completed batch generation: {len(successful_results)} results")
            return successful_results
            
        except Exception as e:
            logger.error(f"❌ Batch generation failed: {str(e)}")
            raise

    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        # Shutdown thread pool
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)
