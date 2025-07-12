import google.generativeai as genai
import os
import json
import re
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

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
    ) -> List[Dict[str, Any]]:

        # Filter ingredients based on dietary restrictions
        allowed_ingredients, protein_suggestions = self._filter_ingredients_by_diet(
            ingredients, dietary_preferences
        )

        prompt = self._build_prompt(
            allowed_ingredients,
            dietary_preferences,
            cuisine_type,
            meal_type,
            protein_suggestions,
        )

        try:
            response = self.model.generate_content(prompt)
            recipes_data = self._parse_response(response.text)

            # Validate recipes against dietary restrictions
            validated_recipes = self._validate_recipes_against_diet(
                recipes_data, dietary_preferences
            )

            return validated_recipes
        except Exception as e:
            # Fallback to sample recipes if AI fails
            return self._get_fallback_recipes(allowed_ingredients, dietary_preferences)

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
