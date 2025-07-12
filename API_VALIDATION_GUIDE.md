# API Parameter Validation with Pydantic

## Overview

The AI Recipe Generator API now implements comprehensive parameter validation using Pydantic. This ensures data integrity, security, and provides clear error messages for invalid requests.

## 🔧 Implementation Features

### 1. **Enhanced Pydantic Schemas**
- **Field constraints** with `Field()` for length, range, and format validation
- **Custom validators** with `@validator` decorators for complex validation logic
- **Root validators** with `@root_validator` for cross-field validation
- **Proper error messages** with descriptive feedback

### 2. **Comprehensive Validation Rules**

#### **Recipe Generation (`/recipes/generate`)**
- **Ingredients**: 1-30 items, no duplicates, valid characters only
- **Dietary preferences**: Must be from predefined list (vegetarian, vegan, gluten-free, etc.)
- **Cuisine type**: Must be from predefined list (italian, chinese, mexican, etc.)
- **Meal type**: Must be from predefined list (breakfast, lunch, dinner, etc.)

#### **Recipe Creation (`/recipes`)**
- **Title**: 3-200 characters, no empty strings
- **Instructions**: Minimum 10 characters
- **Ingredients**: 1-50 items with name, amount, and unit validation
- **Prep/Cook time**: 0-600 minutes for prep, 0-1440 minutes for cook
- **Servings**: 1-20 people
- **Difficulty**: Easy, Medium, Hard, or Expert

#### **Pagination Parameters**
- **Skip**: 0-10,000 (non-negative)
- **Limit**: 1-1,000 (reasonable bounds)

#### **Search Parameters**
- **Query**: Max 200 characters, no dangerous characters
- **Rating**: 1.0-5.0 range
- **Time filters**: Reasonable time bounds

#### **Recipe Rating**
- **Rating**: 1.0-5.0, rounded to 1 decimal place
- **Proper request body validation**

#### **Meal Plans**
- **Name**: 3-100 characters
- **Days**: Must be valid day names (monday-sunday)
- **Recipe IDs**: Positive integers, max 10 per day

#### **ID Parameters**
- **All IDs**: Must be positive integers

### 3. **Custom Exception Handlers**

#### **Validation Error Handler**
```python
{
    "detail": "Validation failed",
    "error_type": "validation_error",
    "field_errors": {
        "ingredients": ["At least one ingredient is required"],
        "dietary_preferences": ["Invalid dietary preference: invalid-diet"]
    }
}
```

#### **HTTP Error Handler**
```python
{
    "detail": "Recipe not found",
    "error_type": "http_error",
    "status_code": 404
}
```

#### **Server Error Handler**
```python
{
    "detail": "Internal server error",
    "error_type": "server_error"
}
```

## 🔍 Validation Examples

### ✅ Valid Recipe Generation Request
```json
{
    "ingredients": ["chicken", "rice", "vegetables"],
    "dietary_preferences": ["gluten-free"],
    "cuisine_type": "italian",
    "meal_type": "dinner"
}
```

### ❌ Invalid Recipe Generation Request
```json
{
    "ingredients": [],
    "dietary_preferences": ["invalid-diet"],
    "cuisine_type": "nonexistent-cuisine"
}
```

**Error Response:**
```json
{
    "detail": "Validation failed",
    "error_type": "validation_error",
    "field_errors": {
        "ingredients": ["At least one ingredient is required"],
        "dietary_preferences": ["Invalid dietary preference: invalid-diet"],
        "cuisine_type": ["Invalid cuisine type: nonexistent-cuisine"]
    }
}
```

### ✅ Valid Meal Plan Creation
```json
{
    "name": "Weekly Meal Plan",
    "recipes": {
        "monday": [1, 2, 3],
        "tuesday": [4, 5],
        "wednesday": [6]
    }
}
```

### ❌ Invalid Meal Plan Creation
```json
{
    "name": "MP",
    "recipes": {
        "invalidday": [0, -1]
    }
}
```

**Error Response:**
```json
{
    "detail": "Validation failed",
    "error_type": "validation_error",
    "field_errors": {
        "name": ["Meal plan name must be at least 3 characters long"],
        "recipes": ["Invalid day: invalidday", "Invalid recipe ID: 0"]
    }
}
```

## 🧪 Testing Validation

Run the validation test script:
```bash
python test_validation.py
```

This will test all validation scenarios and show you how the API handles invalid data.

## 🚀 API Endpoints with Validation

### Recipe Endpoints
- `POST /api/recipes/generate` - Generate recipes with ingredient validation
- `POST /api/recipes/validate-diet` - Validate dietary restrictions
- `GET /api/recipes` - Get recipes with pagination validation
- `GET /api/recipes/search` - Search recipes with parameter validation
- `GET /api/recipes/{id}` - Get specific recipe with ID validation
- `POST /api/recipes` - Create recipe with comprehensive validation
- `PUT /api/recipes/{id}/rating` - Rate recipe with rating validation
- `DELETE /api/recipes/{id}` - Delete recipe with ID validation

### Meal Plan Endpoints
- `POST /api/meal-plans` - Create meal plan with comprehensive validation
- `GET /api/meal-plans` - Get meal plans with pagination validation
- `GET /api/meal-plans/{id}` - Get specific meal plan with ID validation
- `DELETE /api/meal-plans/{id}` - Delete meal plan with ID validation

### Stats Endpoints
- `GET /api/stats` - Get statistics (no special validation needed)

## 🛡️ Security Features

### Input Sanitization
- **Character filtering**: Removes potentially dangerous characters
- **Length limits**: Prevents buffer overflow attacks
- **Format validation**: Ensures proper data formats

### Data Integrity
- **Type checking**: Ensures correct data types
- **Range validation**: Prevents out-of-bounds values
- **Duplicate detection**: Prevents duplicate entries where inappropriate

### Error Handling
- **Consistent error format**: All errors follow the same structure
- **Detailed field errors**: Shows exactly which fields failed validation
- **Logging**: All validation errors are logged for monitoring

## 📋 Predefined Valid Values

### Dietary Preferences
- vegetarian, vegan, gluten-free, dairy-free, nut-free
- low-carb, keto, paleo, mediterranean, halal, kosher
- low-sodium, low-fat, high-protein, diabetic-friendly

### Cuisine Types
- italian, chinese, mexican, indian, french, japanese
- thai, american, mediterranean, greek, spanish, korean
- middle-eastern, british, german, vietnamese, turkish
- moroccan, brazilian, caribbean, african, fusion

### Meal Types
- breakfast, lunch, dinner, snack, dessert, appetizer
- main-course, side-dish, soup, salad, drink, brunch

### Difficulty Levels
- Easy, Medium, Hard, Expert

### Valid Units
- g, kg, ml, l, cup, cups, tbsp, tsp, oz, lb, lbs
- piece, pieces, slice, slices, clove, cloves, bunch
- can, bottle, jar, packet, pinch, dash
- medium, large, small

## 🔄 Usage in Frontend

The frontend can now handle validation errors gracefully:

```javascript
try {
    const response = await axios.post('/api/recipes/generate', data);
    // Handle success
} catch (error) {
    if (error.response?.data?.field_errors) {
        // Display field-specific errors
        const fieldErrors = error.response.data.field_errors;
        Object.entries(fieldErrors).forEach(([field, errors]) => {
            console.log(`${field}: ${errors.join(', ')}`);
        });
    }
}
```

This comprehensive validation system ensures that your API is robust, secure, and provides excellent developer experience with clear error messages!
