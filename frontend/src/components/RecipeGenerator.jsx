import React, { useState } from 'react';
import styled from 'styled-components';
import IngredientInput from './IngredientInput';
import { LoadingWave } from './LoadingIndicators';

const Container = styled.div`
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  margin-bottom: 30px;
`;

const Title = styled.h2`
  color: #333;
  margin-bottom: 20px;
  font-size: 1.8rem;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const Label = styled.label`
  font-weight: 600;
  color: #555;
`;

const Select = styled.select`
  padding: 12px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 16px;
  background: white;
  transition: border-color 0.3s ease;

  &:focus {
    outline: none;
    border-color: #667eea;
  }
`;

const CheckboxContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-top: 10px;
`;

const CheckboxLabel = styled.label`
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-weight: normal;
`;

const Checkbox = styled.input`
  width: 18px;
  height: 18px;
  accent-color: #667eea;
`;

const GenerateButton = styled.button`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 15px 30px;
  border-radius: 8px;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  align-self: flex-start;
  display: flex;
  align-items: center;
  gap: 10px;

  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const WarningBox = styled.div`
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 8px;
  padding: 15px;
  margin: 10px 0;
  color: #856404;
  
  strong {
    color: #6c5500;
  }
`;

const ConflictItem = styled.div`
  padding: 5px 0;
  font-size: 14px;
`;

const dietaryOptions = [
  'Vegetarian', 'Vegan', 'Gluten-Free', 'Dairy-Free', 
  'Keto', 'Low-Carb', 'High-Protein', 'Paleo'
];

const cuisineTypes = [
  'Italian', 'Mexican', 'Chinese', 'Indian', 'Thai', 
  'Mediterranean', 'Japanese', 'French', 'American', 'Korean'
];

const mealTypes = ['Breakfast', 'Lunch', 'Dinner', 'Snack', 'Dessert'];

function RecipeGenerator({ onGenerate, loading, addNotification }) {
  const [ingredients, setIngredients] = useState([]);
  const [dietaryPreferences, setDietaryPreferences] = useState([]);
  const [cuisineType, setCuisineType] = useState('');
  const [mealType, setMealType] = useState('');

  // Dietary restriction mappings
  const dietaryRestrictions = {
    'vegetarian': ['chicken', 'beef', 'pork', 'lamb', 'turkey', 'duck', 'fish', 'salmon', 'tuna', 'shrimp', 'crab', 'lobster', 'meat', 'bacon', 'ham', 'sausage', 'pepperoni'],
    'vegan': ['chicken', 'beef', 'pork', 'lamb', 'turkey', 'duck', 'fish', 'salmon', 'tuna', 'shrimp', 'crab', 'lobster', 'meat', 'bacon', 'ham', 'sausage', 'pepperoni', 'eggs', 'milk', 'cheese', 'butter', 'yogurt', 'cream'],
    'gluten-free': ['wheat', 'barley', 'rye', 'flour', 'bread', 'pasta', 'noodles', 'soy sauce'],
    'dairy-free': ['milk', 'cheese', 'butter', 'yogurt', 'cream', 'ice cream']
  };

  // Check for ingredient conflicts with dietary preferences
  const checkDietaryConflicts = () => {
    const conflicts = [];
    
    dietaryPreferences.forEach(diet => {
      const dietLower = diet.toLowerCase();
      if (dietaryRestrictions[dietLower]) {
        const forbiddenIngredients = dietaryRestrictions[dietLower];
        const conflictingIngredients = ingredients.filter(ingredient => 
          forbiddenIngredients.some(forbidden => 
            ingredient.toLowerCase().includes(forbidden.toLowerCase())
          )
        );
        
        if (conflictingIngredients.length > 0) {
          conflicts.push({
            diet: diet,
            ingredients: conflictingIngredients
          });
        }
      }
    });
    
    return conflicts;
  };

  const conflicts = checkDietaryConflicts();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (ingredients.length === 0) {
      addNotification('Please add at least one ingredient', 'warning');
      return;
    }

    try {
      await onGenerate({
        ingredients,
        dietary_preferences: dietaryPreferences,
        cuisine_type: cuisineType || null,
        meal_type: mealType || null
      });
    } catch (error) {
      addNotification(`❌ Failed to generate recipes: ${error.userMessage || error.message}`, 'error');
    }
  };

  const handleDietaryChange = (option) => {
    setDietaryPreferences(prev => 
      prev.includes(option) 
        ? prev.filter(item => item !== option)
        : [...prev, option]
    );
  };

  return (
    <Container>
      <Title>🥗 Generate New Recipes</Title>
      <Form onSubmit={handleSubmit}>
        <FormGroup>
          <Label>Ingredients *</Label>
          <IngredientInput 
            ingredients={ingredients} 
            onChange={setIngredients} 
          />
        </FormGroup>

        <FormGroup>
          <Label>Cuisine Type (Optional)</Label>
          <Select 
            value={cuisineType} 
            onChange={(e) => setCuisineType(e.target.value)}
          >
            <option value="">Any cuisine</option>
            {cuisineTypes.map(cuisine => (
              <option key={cuisine} value={cuisine}>{cuisine}</option>
            ))}
          </Select>
        </FormGroup>

        <FormGroup>
          <Label>Meal Type (Optional)</Label>
          <Select 
            value={mealType} 
            onChange={(e) => setMealType(e.target.value)}
          >
            <option value="">Any meal</option>
            {mealTypes.map(meal => (
              <option key={meal} value={meal}>{meal}</option>
            ))}
          </Select>
        </FormGroup>

        <FormGroup>
          <Label>Dietary Preferences (Optional)</Label>
          <CheckboxContainer>
            {dietaryOptions.map(option => (
              <CheckboxLabel key={option}>
                <Checkbox
                  type="checkbox"
                  checked={dietaryPreferences.includes(option)}
                  onChange={() => handleDietaryChange(option)}
                />
                {option}
              </CheckboxLabel>
            ))}
          </CheckboxContainer>
        </FormGroup>

        {conflicts.length > 0 && (
          <WarningBox>
            <strong>Warning:</strong> Your ingredient list conflicts with the following dietary preferences:
            {conflicts.map(conflict => (
              <ConflictItem key={conflict.diet}>
                - {conflict.diet}: {conflict.ingredients.join(', ')}
              </ConflictItem>
            ))}
          </WarningBox>
        )}

        <GenerateButton type="submit" disabled={loading}>
          {loading ? (
            <>
              <LoadingWave color="white" />
              <span style={{ marginLeft: '10px' }}>Generating recipes...</span>
            </>
          ) : (
            '🚀 Generate Recipes'
          )}
        </GenerateButton>
      </Form>
    </Container>
  );
}

export default RecipeGenerator;
