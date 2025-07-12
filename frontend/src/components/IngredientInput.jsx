import React, { useState } from 'react';
import styled from 'styled-components';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 10px;
`;

const InputContainer = styled.div`
  display: flex;
  gap: 10px;
  align-items: center;
`;

const Input = styled.input`
  flex: 1;
  padding: 12px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s ease;

  &:focus {
    outline: none;
    border-color: #667eea;
  }
`;

const AddButton = styled.button`
  background: #667eea;
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.3s ease;

  &:hover {
    background: #5a67d8;
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const IngredientsList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
`;

const IngredientTag = styled.span`
  background: #667eea;
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const RemoveButton = styled.button`
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 16px;
  padding: 0;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    background: rgba(255, 255, 255, 0.2);
  }
`;

const SuggestionsList = styled.div`
  background: white;
  border: 1px solid #e1e5e9;
  border-radius: 8px;
  max-height: 200px;
  overflow-y: auto;
  margin-top: 5px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
`;

const SuggestionItem = styled.div`
  padding: 10px 15px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;

  &:hover {
    background: #f8f9fa;
  }

  &:last-child {
    border-bottom: none;
  }
`;

// Common ingredients for suggestions
const commonIngredients = [
  'tomatoes', 'onions', 'garlic', 'olive oil', 'salt', 'pepper',
  'chicken', 'beef', 'fish', 'eggs', 'milk', 'cheese', 'butter',
  'rice', 'pasta', 'bread', 'potatoes', 'carrots', 'bell peppers',
  'mushrooms', 'spinach', 'lettuce', 'basil', 'oregano', 'thyme',
  'lemon', 'lime', 'ginger', 'soy sauce', 'honey', 'vinegar'
];

function IngredientInput({ ingredients, onChange }) {
  const [inputValue, setInputValue] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);

  const handleInputChange = (e) => {
    const value = e.target.value;
    setInputValue(value);

    if (value.length > 1) {
      const filtered = commonIngredients.filter(ingredient =>
        ingredient.toLowerCase().includes(value.toLowerCase()) &&
        !ingredients.includes(ingredient)
      );
      setSuggestions(filtered.slice(0, 5));
      setShowSuggestions(true);
    } else {
      setShowSuggestions(false);
    }
  };

  const addIngredient = (ingredient = inputValue) => {
    const trimmed = ingredient.trim();
    if (trimmed && !ingredients.includes(trimmed)) {
      onChange([...ingredients, trimmed]);
      setInputValue('');
      setShowSuggestions(false);
    }
  };

  const removeIngredient = (ingredient) => {
    onChange(ingredients.filter(item => item !== ingredient));
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addIngredient();
    }
  };

  const handleSuggestionClick = (suggestion) => {
    addIngredient(suggestion);
  };

  return (
    <Container>
      <InputContainer>
        <div style={{ position: 'relative', flex: 1 }}>
          <Input
            type="text"
            value={inputValue}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            placeholder="Type an ingredient (e.g., tomatoes, chicken, rice...)"
            onBlur={() => setTimeout(() => setShowSuggestions(false), 150)}
            onFocus={() => inputValue.length > 1 && setShowSuggestions(true)}
          />
          
          {showSuggestions && suggestions.length > 0 && (
            <SuggestionsList>
              {suggestions.map((suggestion, index) => (
                <SuggestionItem
                  key={index}
                  onClick={() => handleSuggestionClick(suggestion)}
                >
                  {suggestion}
                </SuggestionItem>
              ))}
            </SuggestionsList>
          )}
        </div>
        
        <AddButton 
          type="button" 
          onClick={() => addIngredient()}
          disabled={!inputValue.trim()}
        >
          Add
        </AddButton>
      </InputContainer>

      {ingredients.length > 0 && (
        <IngredientsList>
          {ingredients.map((ingredient, index) => (
            <IngredientTag key={index}>
              {ingredient}
              <RemoveButton onClick={() => removeIngredient(ingredient)}>
                ×
              </RemoveButton>
            </IngredientTag>
          ))}
        </IngredientsList>
      )}
    </Container>
  );
}

export default IngredientInput;
