import React, { useState } from 'react';
import styled from 'styled-components';

const Card = styled.div`
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  transition: transform 0.2s ease, box-shadow 0.2s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 25px rgba(0,0,0,0.15);
  }
`;

const Title = styled.h3`
  color: #333;
  margin-bottom: 10px;
  font-size: 1.3rem;
  line-height: 1.4;
`;

const Description = styled.p`
  color: #666;
  margin-bottom: 15px;
  font-size: 0.9rem;
  line-height: 1.5;
`;

const MetaInfo = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 15px;
  font-size: 0.85rem;
  color: #777;
`;

const MetaItem = styled.span`
  display: flex;
  align-items: center;
  gap: 5px;
`;

const IngredientsSection = styled.div`
  margin-bottom: 15px;
`;

const IngredientsTitle = styled.h4`
  color: #555;
  margin-bottom: 8px;
  font-size: 0.9rem;
`;

const IngredientsList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 5px;
`;

const IngredientItem = styled.li`
  font-size: 0.8rem;
  color: #666;
  padding: 2px 0;
`;

const InstructionsSection = styled.div`
  margin-bottom: 20px;
`;

const InstructionsTitle = styled.h4`
  color: #555;
  margin-bottom: 8px;
  font-size: 0.9rem;
`;

const Instructions = styled.div`
  font-size: 0.85rem;
  color: #666;
  line-height: 1.6;
  max-height: 120px;
  overflow-y: auto;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 6px;
`;

const ActionsContainer = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
`;

const RatingContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
`;

const Stars = styled.div`
  display: flex;
  gap: 2px;
`;

const Star = styled.button`
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: ${props => props.filled ? '#ffc107' : '#ddd'};
  transition: color 0.2s ease;

  &:hover {
    color: #ffc107;
  }
`;

const RatingText = styled.span`
  font-size: 0.85rem;
  color: #666;
`;

const DeleteButton = styled.button`
  background: #dc3545;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: background-color 0.2s ease;

  &:hover {
    background: #c82333;
  }
`;

const SaveButton = styled.button`
  background: #28a745;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: background-color 0.2s ease;

  &:hover {
    background: #218838;
  }
`;

const DiscardButton = styled.button`
  background: #6c757d;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: background-color 0.2s ease;

  &:hover {
    background: #5a6268;
  }
`;

const SaveDiscardActions = styled.div`
  display: flex;
  gap: 10px;
`;

const DifficultyBadge = styled.span`
  background: ${props => {
    switch(props.difficulty?.toLowerCase()) {
      case 'easy': return '#28a745';
      case 'medium': return '#ffc107';
      case 'hard': return '#dc3545';
      default: return '#6c757d';
    }
  }};
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
`;

function RecipeCard({ recipe, onDelete, onRate, onSave, onDiscard, showSaveOptions = false }) {
  const [currentRating, setCurrentRating] = useState(recipe.rating || 0);
  const [hoverRating, setHoverRating] = useState(0);

  const handleRating = (rating) => {
    setCurrentRating(rating);
    if (onRate) {
      onRate(recipe.id, rating);
    }
  };

  const formatInstructions = (instructions) => {
    if (!instructions) return '';
    
    // Handle both array and string formats
    if (Array.isArray(instructions)) {
      // If it's already an array, just join with newlines
      return instructions
        .map((step, index) => {
          // Remove existing numbering if present and add our own
          const cleanStep = step.replace(/^\d+\.\s*/, '').trim();
          return `${index + 1}. ${cleanStep}`;
        })
        .join('\n');
    }
    
    // Handle string format (legacy support)
    if (typeof instructions === 'string') {
      // Split by numbers at the start of lines or by periods followed by space and capital letter
      const steps = instructions
        .split(/(?:\d+\.\s*|\.\s+(?=[A-Z]))/)
        .filter(step => step.trim().length > 0)
        .map((step, index) => `${index + 1}. ${step.trim()}`)
        .join('\n');
      
      return steps;
    }
    
    return '';
  };

  return (
    <Card>
      <Title>{recipe.title}</Title>
      
      {recipe.description && (
        <Description>{recipe.description}</Description>
      )}

      <MetaInfo>
        {recipe.prep_time && (
          <MetaItem>
            ⏱️ Prep: {recipe.prep_time}min
          </MetaItem>
        )}
        {recipe.cook_time && (
          <MetaItem>
            🔥 Cook: {recipe.cook_time}min
          </MetaItem>
        )}
        {recipe.servings && (
          <MetaItem>
            👥 Serves: {recipe.servings}
          </MetaItem>
        )}
        {recipe.difficulty && (
          <MetaItem>
            <DifficultyBadge difficulty={recipe.difficulty}>
              {recipe.difficulty}
            </DifficultyBadge>
          </MetaItem>
        )}
      </MetaInfo>

      {recipe.ingredients && recipe.ingredients.length > 0 && (
        <IngredientsSection>
          <IngredientsTitle>🥗 Ingredients</IngredientsTitle>
          <IngredientsList>
            {recipe.ingredients.map((ingredient, index) => (
              <IngredientItem key={index}>
                • {typeof ingredient === 'string' ? ingredient : 
                   `${ingredient.amount || ''} ${ingredient.unit || ''} ${ingredient.name || ''}`.trim()}
              </IngredientItem>
            ))}
          </IngredientsList>
        </IngredientsSection>
      )}

      <InstructionsSection>
        <InstructionsTitle>📝 Instructions</InstructionsTitle>
        <Instructions>
          {formatInstructions(recipe.instructions)}
        </Instructions>
      </InstructionsSection>

      <ActionsContainer>
        {!showSaveOptions && (
          <RatingContainer>
            <Stars>
              {[1, 2, 3, 4, 5].map((star) => (
                <Star
                  key={star}
                  filled={star <= (hoverRating || currentRating)}
                  onClick={() => handleRating(star)}
                  onMouseEnter={() => setHoverRating(star)}
                  onMouseLeave={() => setHoverRating(0)}
                >
                  ★
                </Star>
              ))}
            </Stars>
            <RatingText>
              {currentRating > 0 ? `${currentRating}/5` : 'Rate this recipe'}
            </RatingText>
          </RatingContainer>
        )}

        {showSaveOptions ? (
          <SaveDiscardActions>
            <SaveButton onClick={onSave}>
              💾 Save
            </SaveButton>
            <DiscardButton onClick={onDiscard}>
              🗑️ Discard
            </DiscardButton>
          </SaveDiscardActions>
        ) : (
          <DeleteButton onClick={() => onDelete(recipe.id)}>
            🗑️ Delete
          </DeleteButton>
        )}
      </ActionsContainer>
    </Card>
  );
}

export default RecipeCard;
