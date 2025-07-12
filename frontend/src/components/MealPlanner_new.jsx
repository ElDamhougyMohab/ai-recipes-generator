import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { mealPlanAPI, recipeAPI } from '../services/api';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

const Container = styled.div`
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
`;

const Title = styled.h2`
  color: #333;
  margin-bottom: 20px;
  font-size: 1.8rem;
`;

const PlannerGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 15px;
  margin-bottom: 30px;
`;

const DayCard = styled.div`
  background: #f8f9fa;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  padding: 15px;
  min-height: 200px;
  transition: border-color 0.3s ease;

  &:hover {
    border-color: #667eea;
  }
`;

const DayTitle = styled.h3`
  color: #333;
  margin-bottom: 15px;
  font-size: 1rem;
  text-align: center;
  padding-bottom: 10px;
  border-bottom: 1px solid #dee2e6;
`;

const MealSlot = styled.div`
  margin-bottom: 10px;
  padding: 8px;
  background: white;
  border-radius: 6px;
  border: 1px dashed #ccc;
  min-height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  color: #666;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    border-color: #667eea;
    background: #f0f4ff;
  }
`;

const RecipeInSlot = styled.div`
  background: #667eea;
  color: white;
  padding: 8px;
  border-radius: 6px;
  font-size: 0.8rem;
  text-align: center;
  cursor: pointer;
  position: relative;

  &:hover {
    background: #5a67d8;
  }
`;

const RemoveButton = styled.button`
  position: absolute;
  top: -5px;
  right: -5px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    background: #c82333;
  }
`;

const RecipeSelector = styled.div`
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  max-height: 300px;
  overflow-y: auto;
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  z-index: 10;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
`;

const RecipeOption = styled.div`
  padding: 12px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  font-size: 0.85rem;

  &:hover {
    background: #f8f9fa;
  }

  &:last-child {
    border-bottom: none;
  }
`;

const SaveButton = styled.button`
  background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(40, 167, 69, 0.4);
  }
`;

const EmptyState = styled.div`
  text-align: center;
  color: #666;
  padding: 40px;
  font-size: 1.1rem;
`;

const SavedPlansSection = styled.div`
  margin-top: 40px;
  padding-top: 30px;
  border-top: 2px solid #f0f0f0;
`;

const SavedPlanCard = styled.div`
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 15px;
  transition: all 0.2s ease;

  &:hover {
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    transform: translateY(-2px);
  }
`;

const PlanHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
`;

const PlanTitle = styled.h3`
  margin: 0;
  color: #333;
`;

const PlanDate = styled.span`
  color: #666;
  font-size: 0.9rem;
`;

const LoadButton = styled.button`
  background: #667eea;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  margin-right: 10px;

  &:hover {
    background: #5a67d8;
  }
`;

const DeleteButton = styled.button`
  background: #dc3545;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;

  &:hover {
    background: #c82333;
  }
`;

const ExportButton = styled.button`
  background: #17a2b8;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  margin-right: 10px;

  &:hover {
    background: #138496;
  }
`;

const PlanSummary = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 10px;
  margin-top: 10px;
`;

const DaySummary = styled.div`
  background: white;
  padding: 10px;
  border-radius: 6px;
  border: 1px solid #e9ecef;
`;

const DayName = styled.div`
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
  font-size: 0.8rem;
`;

const MealCount = styled.div`
  color: #666;
  font-size: 0.7rem;
`;

const InputGroup = styled.div`
  margin-bottom: 20px;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
  color: #333;
`;

const Input = styled.input`
  width: 100%;
  padding: 12px;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  font-size: 16px;
  
  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-top: 20px;
`;

const SecondaryButton = styled.button`
  background: #6c757d;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: #5a6268;
    transform: translateY(-1px);
  }
`;

const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const mealTimes = ['Breakfast', 'Lunch', 'Dinner'];

function MealPlanner({ recipes }) {
  const [mealPlan, setMealPlan] = useState(
    days.reduce((acc, day) => {
      acc[day] = mealTimes.reduce((meals, meal) => {
        meals[meal] = null;
        return meals;
      }, {});
      return acc;
    }, {})
  );
  
  const [showSelector, setShowSelector] = useState(null);
  const [savedPlans, setSavedPlans] = useState([]);
  const [planName, setPlanName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const pdfRef = useRef(null);

  useEffect(() => {
    loadSavedPlans();
  }, []);

  const loadSavedPlans = async () => {
    try {
      const plans = await mealPlanAPI.getMealPlans();
      setSavedPlans(plans);
    } catch (error) {
      console.error('Error loading meal plans:', error);
    }
  };

  const addRecipeToSlot = (day, mealTime, recipe) => {
    setMealPlan(prev => ({
      ...prev,
      [day]: {
        ...prev[day],
        [mealTime]: recipe
      }
    }));
    setShowSelector(null);
  };

  const removeRecipeFromSlot = (day, mealTime) => {
    setMealPlan(prev => ({
      ...prev,
      [day]: {
        ...prev[day],
        [mealTime]: null
      }
    }));
  };

  const saveMealPlan = async () => {
    if (!planName.trim()) {
      alert('Please enter a name for your meal plan');
      return;
    }

    setIsLoading(true);
    try {
      // First, save any temporary recipes to the database
      const tempRecipes = [];
      const savedRecipeIds = [];

      for (const day of days) {
        for (const mealTime of mealTimes) {
          const recipe = mealPlan[day][mealTime];
          if (recipe && typeof recipe.id === 'string' && recipe.id.startsWith('temp_')) {
            tempRecipes.push(recipe);
          }
        }
      }

      // Save temporary recipes first
      for (const tempRecipe of tempRecipes) {
        try {
          const recipeData = {
            title: tempRecipe.title,
            description: tempRecipe.description || '',
            instructions: tempRecipe.instructions,
            ingredients: tempRecipe.ingredients,
            prep_time: tempRecipe.prep_time,
            cook_time: tempRecipe.cook_time,
            servings: tempRecipe.servings,
            difficulty: tempRecipe.difficulty
          };

          const savedRecipe = await recipeAPI.createRecipe(recipeData);
          savedRecipeIds.push({ tempId: tempRecipe.id, savedId: savedRecipe.id });
        } catch (error) {
          console.error('Error saving temporary recipe:', error);
        }
      }

      // Update meal plan with saved recipe IDs
      const updatedMealPlan = { ...mealPlan };
      for (const day of days) {
        for (const mealTime of mealTimes) {
          const recipe = updatedMealPlan[day][mealTime];
          if (recipe && typeof recipe.id === 'string' && recipe.id.startsWith('temp_')) {
            const savedRecipe = savedRecipeIds.find(r => r.tempId === recipe.id);
            if (savedRecipe) {
              updatedMealPlan[day][mealTime] = { ...recipe, id: savedRecipe.savedId };
            }
          }
        }
      }

      // Convert meal plan to API format
      const planData = {
        name: planName,
        recipes: Object.keys(updatedMealPlan).reduce((acc, day) => {
          const dayRecipes = Object.values(updatedMealPlan[day])
            .filter(recipe => recipe !== null)
            .map(recipe => recipe.id);
          
          if (dayRecipes.length > 0) {
            acc[day] = dayRecipes;
          }
          return acc;
        }, {})
      };

      const savedPlan = await mealPlanAPI.createMealPlan(planData);
      
      // Update the current meal plan with saved recipe IDs
      setMealPlan(updatedMealPlan);
      
      // Reload saved plans to show the new one
      await loadSavedPlans();
      
      // Reset form
      setPlanName('');
      
      alert('Meal plan saved successfully!');
    } catch (error) {
      console.error('Error saving meal plan:', error);
      alert('Error saving meal plan. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const loadMealPlan = async (plan) => {
    try {
      // Convert saved plan back to component format
      const loadedPlan = days.reduce((acc, day) => {
        acc[day] = mealTimes.reduce((meals, meal) => {
          meals[meal] = null;
          return meals;
        }, {});
        return acc;
      }, {});

      // Load recipes for each day
      for (const [day, recipeIds] of Object.entries(plan.recipes)) {
        if (recipeIds && recipeIds.length > 0) {
          const dayRecipes = recipeIds.map(id => 
            recipes.find(r => r.id === id)
          ).filter(Boolean);
          
          dayRecipes.forEach((recipe, index) => {
            if (index < mealTimes.length) {
              loadedPlan[day][mealTimes[index]] = recipe;
            }
          });
        }
      }

      setMealPlan(loadedPlan);
      setPlanName(plan.name);
    } catch (error) {
      console.error('Error loading meal plan:', error);
      alert('Error loading meal plan. Please try again.');
    }
  };

  const clearMealPlan = () => {
    setMealPlan(days.reduce((acc, day) => {
      acc[day] = mealTimes.reduce((meals, meal) => {
        meals[meal] = null;
        return meals;
      }, {});
      return acc;
    }, {}));
    setPlanName('');
  };

  const deleteMealPlan = async (planId) => {
    if (!window.confirm('Are you sure you want to delete this meal plan?')) {
      return;
    }

    try {
      await mealPlanAPI.deleteMealPlan(planId);
      await loadSavedPlans();
      alert('Meal plan deleted successfully!');
    } catch (error) {
      console.error('Error deleting meal plan:', error);
      alert('Error deleting meal plan. Please try again.');
    }
  };

  const exportToPDF = async (plan = null) => {
    try {
      const planToExport = plan || { name: planName || 'Current Meal Plan', recipes: mealPlan };
      
      // Get unique recipes and ingredients
      const uniqueRecipes = [];
      const allIngredients = new Map();
      
      // Process meal plan to get recipes and ingredients
      if (plan) {
        // For saved plans, we need to get the actual recipe objects
        for (const [day, recipeIds] of Object.entries(plan.recipes)) {
          for (const recipeId of recipeIds) {
            const recipe = recipes.find(r => r.id === recipeId);
            if (recipe && !uniqueRecipes.find(r => r.id === recipe.id)) {
              uniqueRecipes.push(recipe);
              
              // Add ingredients to shopping list
              if (recipe.ingredients) {
                recipe.ingredients.forEach(ingredient => {
                  const key = typeof ingredient === 'string' ? ingredient : ingredient.name || ingredient.ingredient;
                  const amount = typeof ingredient === 'string' ? '' : ingredient.amount || ingredient.quantity || '';
                  const unit = typeof ingredient === 'string' ? '' : ingredient.unit || '';
                  
                  if (allIngredients.has(key)) {
                    allIngredients.set(key, `${allIngredients.get(key)}, ${amount} ${unit}`.trim());
                  } else {
                    allIngredients.set(key, `${amount} ${unit}`.trim());
                  }
                });
              }
            }
          }
        }
      } else {
        // For current meal plan
        for (const day of days) {
          for (const mealTime of mealTimes) {
            const recipe = mealPlan[day][mealTime];
            if (recipe && !uniqueRecipes.find(r => r.id === recipe.id)) {
              uniqueRecipes.push(recipe);
              
              // Add ingredients to shopping list
              if (recipe.ingredients) {
                recipe.ingredients.forEach(ingredient => {
                  const key = typeof ingredient === 'string' ? ingredient : ingredient.name || ingredient.ingredient;
                  const amount = typeof ingredient === 'string' ? '' : ingredient.amount || ingredient.quantity || '';
                  const unit = typeof ingredient === 'string' ? '' : ingredient.unit || '';
                  
                  if (allIngredients.has(key)) {
                    allIngredients.set(key, `${allIngredients.get(key)}, ${amount} ${unit}`.trim());
                  } else {
                    allIngredients.set(key, `${amount} ${unit}`.trim());
                  }
                });
              }
            }
          }
        }
      }

      // Create PDF content
      const pdf = new jsPDF('p', 'mm', 'a4');
      const pageWidth = pdf.internal.pageSize.width;
      const pageHeight = pdf.internal.pageSize.height;
      let yPosition = 20;
      
      // Title
      pdf.setFontSize(24);
      pdf.setFont('helvetica', 'bold');
      pdf.text(planToExport.name, pageWidth / 2, yPosition, { align: 'center' });
      yPosition += 10;
      
      // Subtitle
      pdf.setFontSize(12);
      pdf.setFont('helvetica', 'normal');
      pdf.text(`Generated on ${new Date().toLocaleDateString()}`, pageWidth / 2, yPosition, { align: 'center' });
      yPosition += 20;
      
      // Weekly Schedule
      pdf.setFontSize(16);
      pdf.setFont('helvetica', 'bold');
      pdf.text('Weekly Meal Schedule', 20, yPosition);
      yPosition += 15;
      
      // Days and meals
      for (let i = 0; i < days.length; i++) {
        const day = days[i];
        
        if (yPosition > pageHeight - 40) {
          pdf.addPage();
          yPosition = 20;
        }
        
        pdf.setFontSize(12);
        pdf.setFont('helvetica', 'bold');
        pdf.text(day, 20, yPosition);
        yPosition += 8;
        
        // Get meals for this day
        const dayMeals = plan ? 
          (plan.recipes[day] || []).map(id => recipes.find(r => r.id === id)).filter(Boolean) :
          mealTimes.map(meal => mealPlan[day][meal]).filter(Boolean);
        
        if (dayMeals.length > 0) {
          dayMeals.forEach((recipe, index) => {
            const mealType = plan ? 
              (index < mealTimes.length ? mealTimes[index] : 'Meal') :
              Object.keys(mealPlan[day]).find(meal => mealPlan[day][meal] === recipe);
            
            pdf.setFontSize(10);
            pdf.setFont('helvetica', 'normal');
            pdf.text(`${mealType}: ${recipe.title}`, 25, yPosition);
            yPosition += 6;
          });
        } else {
          pdf.setFontSize(10);
          pdf.setFont('helvetica', 'italic');
          pdf.text('No meals planned', 25, yPosition);
          yPosition += 6;
        }
        
        yPosition += 5;
      }
      
      // Shopping List
      if (allIngredients.size > 0) {
        if (yPosition > pageHeight - 60) {
          pdf.addPage();
          yPosition = 20;
        }
        
        yPosition += 10;
        pdf.setFontSize(16);
        pdf.setFont('helvetica', 'bold');
        pdf.text('Shopping List', 20, yPosition);
        yPosition += 15;
        
        for (const [ingredient, amount] of allIngredients) {
          if (yPosition > pageHeight - 20) {
            pdf.addPage();
            yPosition = 20;
          }
          
          pdf.setFontSize(10);
          pdf.setFont('helvetica', 'normal');
          pdf.text(`• ${ingredient}${amount ? ` (${amount})` : ''}`, 25, yPosition);
          yPosition += 6;
        }
      }
      
      // Recipe Details
      if (uniqueRecipes.length > 0) {
        pdf.addPage();
        yPosition = 20;
        
        pdf.setFontSize(16);
        pdf.setFont('helvetica', 'bold');
        pdf.text('Recipe Details', 20, yPosition);
        yPosition += 15;
        
        uniqueRecipes.forEach((recipe, index) => {
          if (yPosition > pageHeight - 80) {
            pdf.addPage();
            yPosition = 20;
          }
          
          // Recipe title
          pdf.setFontSize(14);
          pdf.setFont('helvetica', 'bold');
          pdf.text(recipe.title, 20, yPosition);
          yPosition += 10;
          
          // Recipe info
          pdf.setFontSize(9);
          pdf.setFont('helvetica', 'normal');
          const info = [];
          if (recipe.prep_time) info.push(`Prep: ${recipe.prep_time}min`);
          if (recipe.cook_time) info.push(`Cook: ${recipe.cook_time}min`);
          if (recipe.servings) info.push(`Servings: ${recipe.servings}`);
          if (recipe.difficulty) info.push(`Difficulty: ${recipe.difficulty}`);
          
          if (info.length > 0) {
            pdf.text(info.join(' | '), 20, yPosition);
            yPosition += 8;
          }
          
          // Ingredients
          if (recipe.ingredients && recipe.ingredients.length > 0) {
            pdf.setFontSize(10);
            pdf.setFont('helvetica', 'bold');
            pdf.text('Ingredients:', 20, yPosition);
            yPosition += 6;
            
            recipe.ingredients.forEach(ingredient => {
              const text = typeof ingredient === 'string' ? ingredient : 
                `${ingredient.amount || ''} ${ingredient.unit || ''} ${ingredient.name || ingredient.ingredient}`.trim();
              
              pdf.setFontSize(9);
              pdf.setFont('helvetica', 'normal');
              pdf.text(`• ${text}`, 25, yPosition);
              yPosition += 5;
            });
            yPosition += 5;
          }
          
          // Instructions
          if (recipe.instructions) {
            pdf.setFontSize(10);
            pdf.setFont('helvetica', 'bold');
            pdf.text('Instructions:', 20, yPosition);
            yPosition += 6;
            
            pdf.setFontSize(9);
            pdf.setFont('helvetica', 'normal');
            const instructions = recipe.instructions.split('\n');
            instructions.forEach(instruction => {
              if (instruction.trim()) {
                const lines = pdf.splitTextToSize(instruction.trim(), pageWidth - 50);
                lines.forEach(line => {
                  if (yPosition > pageHeight - 20) {
                    pdf.addPage();
                    yPosition = 20;
                  }
                  pdf.text(line, 25, yPosition);
                  yPosition += 5;
                });
              }
            });
          }
          
          yPosition += 10;
        });
      }
      
      // Save the PDF
      const fileName = `${planToExport.name.replace(/[^a-zA-Z0-9]/g, '_')}_meal_plan.pdf`;
      pdf.save(fileName);
      
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Error generating PDF. Please try again.');
    }
  };

  if (recipes.length === 0) {
    return (
      <Container>
        <Title>📅 Weekly Meal Planner</Title>
        <EmptyState>
          No recipes available for meal planning.<br/>
          Generate or save some recipes first!
        </EmptyState>
      </Container>
    );
  }

  return (
    <Container>
      <Title>📅 Weekly Meal Planner</Title>
      
      <InputGroup>
        <Label htmlFor="planName">Meal Plan Name</Label>
        <Input
          id="planName"
          type="text"
          placeholder="Enter a name for your meal plan"
          value={planName}
          onChange={(e) => setPlanName(e.target.value)}
        />
      </InputGroup>
      
      <PlannerGrid>
        {days.map(day => (
          <DayCard key={day}>
            <DayTitle>{day}</DayTitle>
            
            {mealTimes.map(mealTime => (
              <div key={mealTime} style={{ position: 'relative', marginBottom: '10px' }}>
                {mealPlan[day][mealTime] ? (
                  <RecipeInSlot>
                    <div style={{ paddingRight: '15px' }}>
                      <div style={{ fontWeight: 'bold', marginBottom: '2px' }}>
                        {mealTime}
                      </div>
                      {mealPlan[day][mealTime].title}
                    </div>
                    <RemoveButton 
                      onClick={() => removeRecipeFromSlot(day, mealTime)}
                    >
                      ×
                    </RemoveButton>
                  </RecipeInSlot>
                ) : (
                  <MealSlot
                    onClick={() => setShowSelector({ day, mealTime })}
                  >
                    + Add {mealTime}
                  </MealSlot>
                )}
                
                {showSelector?.day === day && showSelector?.mealTime === mealTime && (
                  <RecipeSelector>
                    {recipes.map(recipe => (
                      <RecipeOption
                        key={recipe.id}
                        onClick={() => addRecipeToSlot(day, mealTime, recipe)}
                      >
                        <strong>{recipe.title}</strong>
                        {recipe.prep_time && (
                          <div style={{ color: '#666', fontSize: '0.75rem' }}>
                            Prep: {recipe.prep_time}min
                          </div>
                        )}
                      </RecipeOption>
                    ))}
                  </RecipeSelector>
                )}
              </div>
            ))}
          </DayCard>
        ))}
      </PlannerGrid>

      <ButtonGroup>
        <SecondaryButton onClick={clearMealPlan}>
          🗑️ Clear Plan
        </SecondaryButton>
        <SecondaryButton onClick={() => exportToPDF()}>
          📄 Export PDF
        </SecondaryButton>
        <SaveButton onClick={saveMealPlan} disabled={isLoading}>
          {isLoading ? '⏳ Saving...' : '💾 Save Meal Plan'}
        </SaveButton>
      </ButtonGroup>

      <SavedPlansSection>
        <Title>📋 Saved Meal Plans</Title>
        {savedPlans.length === 0 ? (
          <EmptyState>
            No saved meal plans yet.<br/>
            Create and save your first meal plan above!
          </EmptyState>
        ) : (
          savedPlans.map(plan => (
            <SavedPlanCard key={plan.id}>
              <PlanHeader>
                <div>
                  <PlanTitle>{plan.name}</PlanTitle>
                  <PlanDate>
                    Created: {new Date(plan.created_at).toLocaleDateString()}
                  </PlanDate>
                </div>
                <div>
                  <LoadButton onClick={() => loadMealPlan(plan)}>
                    📥 Load Plan
                  </LoadButton>
                  <ExportButton onClick={() => exportToPDF(plan)}>
                    📄 Export PDF
                  </ExportButton>
                  <DeleteButton onClick={() => deleteMealPlan(plan.id)}>
                    🗑️ Delete
                  </DeleteButton>
                </div>
              </PlanHeader>
              
              <PlanSummary>
                {Object.entries(plan.recipes).map(([day, recipeIds]) => (
                  <DaySummary key={day}>
                    <DayName>{day}</DayName>
                    <MealCount>{recipeIds.length} meals</MealCount>
                  </DaySummary>
                ))}
              </PlanSummary>
            </SavedPlanCard>
          ))
        )}
      </SavedPlansSection>
    </Container>
  );
}

export default MealPlanner;
