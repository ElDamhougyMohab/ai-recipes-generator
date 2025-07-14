import React, { useState } from 'react';
import styled from 'styled-components';
import RecipeGenerator from './components/RecipeGenerator';
import RecipeCard from './components/RecipeCard';
import MealPlanner from './components/MealPlanner';
import ConnectionStatus from './components/ConnectionStatus';
import Pagination from './components/Pagination';
import { useRecipes } from './hooks/useRecipes';
import { LoadingOverlay, SkeletonLoader } from './components/LoadingIndicators';

const AppContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f8f9fa;
  min-height: 100vh;
`;

const Header = styled.header`
  text-align: center;
  margin-bottom: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 40px 20px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
`;

const Title = styled.h1`
  font-size: 2.5rem;
  margin-bottom: 10px;
  font-weight: 700;
`;

const Subtitle = styled.p`
  font-size: 1.2rem;
  opacity: 0.9;
`;

const TabContainer = styled.div`
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
  background: white;
  border-radius: 8px;
  padding: 5px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
`;

const Tab = styled.button`
  padding: 12px 24px;
  border: none;
  background: ${props => props.active ? '#667eea' : 'transparent'};
  color: ${props => props.active ? 'white' : '#666'};
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;

  &:hover {
    background: ${props => props.active ? '#667eea' : '#f0f0f0'};
  }
`;

const RecipesGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 30px;
`;

const NotificationContainer = styled.div`
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  max-width: 400px;
`;

const Notification = styled.div`
  background: ${props => {
    switch(props.type) {
      case 'success': return '#d4edda';
      case 'warning': return '#fff3cd';
      case 'error': return '#f8d7da';
      default: return '#d1ecf1';
    }
  }};
  border: 1px solid ${props => {
    switch(props.type) {
      case 'success': return '#c3e6cb';
      case 'warning': return '#ffeaa7';
      case 'error': return '#f5c6cb';
      default: return '#bee5eb';
    }
  }};
  color: ${props => {
    switch(props.type) {
      case 'success': return '#155724';
      case 'warning': return '#856404';
      case 'error': return '#721c24';
      default: return '#0c5460';
    }
  }};
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 10px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  animation: slideIn 0.3s ease-out;

  @keyframes slideIn {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  float: right;
  font-size: 18px;
  cursor: pointer;
  opacity: 0.7;
  
  &:hover {
    opacity: 1;
  }
`;

const GeneratedRecipesSection = styled.div`
  margin-top: 30px;
`;

const GeneratedRecipesHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
`;

const GeneratedRecipesTitle = styled.h2`
  color: #333;
  margin: 0;
`;

const BulkActions = styled.div`
  display: flex;
  gap: 10px;
`;

const BulkActionButton = styled.button`
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s ease;
  
  &.save-all {
    background: #28a745;
    color: white;
    
    &:hover {
      background: #218838;
    }
  }
  
  &.discard-all {
    background: #dc3545;
    color: white;
    
    &:hover {
      background: #c82333;
    }
  }
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 40px 20px;
  color: #666;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
`;

const EmptyStateIcon = styled.div`
  font-size: 4rem;
  margin-bottom: 20px;
`;

const EmptyStateTitle = styled.h3`
  color: #333;
  margin-bottom: 10px;
`;

const EmptyStateText = styled.p`
  font-size: 1.1rem;
  line-height: 1.6;
`;

const SavedRecipesHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
`;

const SavedRecipesTitle = styled.h2`
  color: #333;
  margin: 0;
`;

const DeleteAllButton = styled.button`
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s ease;
  background: #dc3545;
  color: white;
  
  &:hover {
    background: #c82333;
    transform: translateY(-1px);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`;

const BackgroundIndicator = styled.div`
  position: fixed;
  top: 20px;
  left: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  z-index: 1001;
  display: flex;
  align-items: center;
  gap: 8px;
  animation: pulse 2s infinite;
  
  @keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.7; }
    100% { opacity: 1; }
  }
`;

function App() {
  const [activeTab, setActiveTab] = useState('generate');
  const [notifications, setNotifications] = useState([]);
  const [generatedRecipes, setGeneratedRecipes] = useState([]);
  const [isLoadingRecipes, setIsLoadingRecipes] = useState(false);
  
  // Background recipe generation state
  const [isGeneratingInBackground, setIsGeneratingInBackground] = useState(false);
  const [backgroundGenerationId, setBackgroundGenerationId] = useState(null);
  const { 
    recipes, 
    loading, 
    pagination, 
    generateRecipes, 
    deleteRecipe, 
    rateRecipe, 
    createRecipe, 
    loadRecipes, 
    searchRecipes 
  } = useRecipes();

  const addNotification = (message, type = 'info', duration = 5000) => {
    const id = Date.now() + Math.random(); // Make ID more unique to avoid conflicts
    const notification = { id, message, type };
    
    // Check if notification with same message already exists
    setNotifications(prev => {
      const existingIndex = prev.findIndex(n => n.message === message);
      let newNotifications;
      
      if (existingIndex !== -1) {
        // Remove existing notification with same message
        newNotifications = prev.filter((_, index) => index !== existingIndex).concat(notification);
      } else {
        newNotifications = [...prev, notification];
      }
      
      // Limit to maximum 5 notifications to prevent overflow
      if (newNotifications.length > 5) {
        newNotifications = newNotifications.slice(-5);
      }
      
      return newNotifications;
    });
    
    if (duration > 0) {
      setTimeout(() => {
        removeNotification(id);
      }, duration);
    }
  };

  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(notif => notif.id !== id));
  };

  const clearAllNotifications = () => {
    setNotifications([]);
  };

  // Clear notifications when tab changes
  const handleTabChange = (newTab) => {
    setActiveTab(newTab);
    // Clear old notifications when switching tabs to avoid stuck messages
    clearAllNotifications();
  };

  const handleGenerateRecipes = async (requestData) => {
    // Generate unique ID for this generation request
    const generationId = Date.now().toString();
    
    try {
      setIsGeneratingInBackground(true);
      setBackgroundGenerationId(generationId);
      
      // Show start notification but don't block UI
      addNotification('🚀 Generating recipes in the background... You can continue using the app!', 'info', 4000);
      
      console.log('🚀 Starting background recipe generation with:', requestData);
      
      // Make the API call in the background
      const response = await generateRecipes(requestData);
      
      console.log('✅ Background generation completed:', response);
      
      // Process the response
      const recipeCount = response.recipes ? response.recipes.length : 0;
      
      if (recipeCount > 0) {
        // Add new recipes to the generated recipes list
        setGeneratedRecipes(prev => [...prev, ...(response.recipes || [])]);
        
        // Show success notification
        addNotification(`🎉 Generated ${recipeCount} new recipes! Check the "Generated Recipes" section below.`, 'success', 6000);
      } else {
        addNotification('⚠️ No recipes were generated. Try different ingredients or settings.', 'warning', 5000);
      }
      
      // Check if dietary filtering occurred
      if (response.dietary_filtering && response.dietary_filtering.has_conflicts) {
        const { forbidden_ingredients, protein_suggestions } = response.dietary_filtering;
        
        let message = `⚠️ Filtered out non-compliant ingredients: ${forbidden_ingredients.join(', ')}`;
        if (protein_suggestions.length > 0) {
          message += `. Suggested alternatives: ${protein_suggestions.join(', ')}`;
        }
        
        addNotification(message, 'warning', 8000);
      } else if (response.dietary_filtering) {
        addNotification('✅ All ingredients are compatible with your dietary preferences!', 'success');
      }
      
    } catch (error) {
      console.error('❌ Background generation failed:', error);
      // Always show error messages
      addNotification(`❌ Failed to generate recipes: ${error.userMessage || error.message}`, 'error');
    } finally {
      setIsGeneratingInBackground(false);
      setBackgroundGenerationId(null);
    }
  };

  const handleSaveRecipe = async (recipe) => {
    try {
      setIsLoadingRecipes(true);
      // Create a clean recipe object without temporary fields
      const cleanRecipe = {
        title: recipe.title,
        description: recipe.description,
        instructions: recipe.instructions,
        ingredients: recipe.ingredients,
        prep_time: recipe.prep_time,
        cook_time: recipe.cook_time,
        servings: recipe.servings,
        difficulty: recipe.difficulty
      };
      
      await createRecipe(cleanRecipe);
      // Remove from generated recipes after saving
      setGeneratedRecipes(prev => prev.filter(r => r.id !== recipe.id));
      addNotification('✅ Recipe saved successfully!', 'success');
    } catch (error) {
      addNotification(`❌ Failed to save recipe: ${error.userMessage || error.message}`, 'error');
    } finally {
      setIsLoadingRecipes(false);
    }
  };

  const handleDiscardRecipe = (recipeId) => {
    setGeneratedRecipes(prev => prev.filter(r => r.id !== recipeId));
    addNotification('Recipe discarded', 'info');
  };

  const handleDiscardAll = () => {
    setGeneratedRecipes([]);
    addNotification('All recipes discarded', 'info');
  };

  const handleSaveAll = async () => {
    try {
      setIsLoadingRecipes(true);
      for (const recipe of generatedRecipes) {
        const cleanRecipe = {
          title: recipe.title,
          description: recipe.description,
          instructions: recipe.instructions,
          ingredients: recipe.ingredients,
          prep_time: recipe.prep_time,
          cook_time: recipe.cook_time,
          servings: recipe.servings,
          difficulty: recipe.difficulty
        };
        await createRecipe(cleanRecipe);
      }
      setGeneratedRecipes([]);
      addNotification(`✅ All ${generatedRecipes.length} recipes saved successfully!`, 'success');
    } catch (error) {
      addNotification(`❌ Failed to save all recipes: ${error.message}`, 'error');
    } finally {
      setIsLoadingRecipes(false);
    }
  };

  const handleDeleteAll = async () => {
    if (recipes.length === 0) {
      addNotification('No recipes to delete', 'info');
      return;
    }

    const confirmDelete = window.confirm(
      `Are you sure you want to delete all ${recipes.length} saved recipes? This action cannot be undone.`
    );
    
    if (!confirmDelete) return;

    try {
      for (const recipe of recipes) {
        await deleteRecipe(recipe.id);
      }
      addNotification(`✅ All ${recipes.length} recipes deleted successfully!`, 'success');
    } catch (error) {
      addNotification(`❌ Failed to delete all recipes: ${error.message}`, 'error');
    }
  };

  return (
    <AppContainer>
      {/* Background generation indicator */}
      {isGeneratingInBackground && (
        <BackgroundIndicator>
          ⚡ Generating recipes in background...
        </BackgroundIndicator>
      )}
      
      <Header>
        <Title>🍳 AI Recipe Generator</Title>
        <Subtitle>Discover amazing recipes with artificial intelligence</Subtitle>
      </Header>

      <NotificationContainer>
        {notifications.length > 1 && (
          <div style={{ textAlign: 'right', marginBottom: '8px' }}>
            <button 
              onClick={clearAllNotifications}
              style={{
                background: 'none',
                border: '1px solid #ddd',
                borderRadius: '4px',
                padding: '4px 8px',
                fontSize: '12px',
                cursor: 'pointer',
                color: '#666'
              }}
            >
              Clear All
            </button>
          </div>
        )}
        {notifications.map(notification => (
          <Notification key={notification.id} type={notification.type}>
            <CloseButton onClick={() => removeNotification(notification.id)}>
              ×
            </CloseButton>
            {notification.message}
          </Notification>
        ))}
      </NotificationContainer>

      <TabContainer>
        <Tab 
          active={activeTab === 'generate'} 
          onClick={() => handleTabChange('generate')}
        >
          Generate Recipes
        </Tab>
        <Tab 
          active={activeTab === 'saved'} 
          onClick={() => handleTabChange('saved')}
        >
          Saved Recipes
        </Tab>
        <Tab 
          active={activeTab === 'planner'} 
          onClick={() => handleTabChange('planner')}
        >
          Meal Planner
        </Tab>
      </TabContainer>

      {activeTab === 'generate' && (
        <div>
          <RecipeGenerator 
            onGenerate={handleGenerateRecipes}
            loading={isGeneratingInBackground}
            addNotification={addNotification}
          />
          
          {generatedRecipes.length > 0 && (
            <GeneratedRecipesSection>
              <GeneratedRecipesHeader>
                <GeneratedRecipesTitle>Generated Recipes</GeneratedRecipesTitle>
                <BulkActions>
                  <BulkActionButton 
                    className="save-all"
                    onClick={handleSaveAll}
                  >
                    💾 Save All
                  </BulkActionButton>
                  <BulkActionButton 
                    className="discard-all"
                    onClick={handleDiscardAll}
                  >
                    🗑️ Discard All
                  </BulkActionButton>
                </BulkActions>
              </GeneratedRecipesHeader>
              
              <RecipesGrid>
                {generatedRecipes.map(recipe => (
                  <RecipeCard
                    key={recipe.id}
                    recipe={recipe}
                    onSave={() => handleSaveRecipe(recipe)}
                    onDiscard={() => handleDiscardRecipe(recipe.id)}
                    showSaveOptions={true}
                  />
                ))}
              </RecipesGrid>
            </GeneratedRecipesSection>
          )}
          
          {generatedRecipes.length === 0 && !isGeneratingInBackground && (
            <EmptyState>
              <EmptyStateIcon>🍳</EmptyStateIcon>
              <EmptyStateTitle>Ready to Generate Recipes!</EmptyStateTitle>
              <EmptyStateText>
                Fill in the form above with your ingredients and preferences, then click "Generate Recipes". 
                Recipes will be generated in the background so you can continue using the app!
              </EmptyStateText>
            </EmptyState>
          )}
        </div>
      )}

      {activeTab === 'saved' && (
        <div>
          <SavedRecipesHeader>
            <SavedRecipesTitle>Your Saved Recipes</SavedRecipesTitle>
            <DeleteAllButton 
              onClick={handleDeleteAll}
              disabled={recipes.length === 0}
            >
              🗑️ Delete All
            </DeleteAllButton>
          </SavedRecipesHeader>
          <RecipesGrid>
            {loading && Array.from({ length: 6 }, (_, index) => (
              <SkeletonLoader key={`skeleton-${index}`} lines={4} />
            ))}
            {!loading && recipes.map(recipe => (
              <RecipeCard
                key={recipe.id}
                recipe={recipe}
                onDelete={deleteRecipe}
                onRate={rateRecipe}
              />
            ))}
          </RecipesGrid>
          
          {/* Pagination */}
          {!loading && recipes.length > 0 && (
            <Pagination
              currentPage={pagination.page}
              totalPages={pagination.pages}
              totalItems={pagination.total}
              itemsPerPage={pagination.per_page}
              onPageChange={(page) => loadRecipes(page, pagination.per_page)}
              hasNext={pagination.has_next}
              hasPrev={pagination.has_prev}
              isLoading={loading}
            />
          )}
          
          {!loading && recipes.length === 0 && (
            <EmptyState>
              <EmptyStateIcon>📚</EmptyStateIcon>
              <EmptyStateTitle>No Saved Recipes Yet</EmptyStateTitle>
              <EmptyStateText>
                Generate some recipes to get started! Your saved recipes will appear here.
              </EmptyStateText>
            </EmptyState>
          )}
        </div>
      )}

      {activeTab === 'planner' && (
        <MealPlanner addNotification={addNotification} />
      )}



      {/* Recipe Saving Overlay */}
      {isLoadingRecipes && (
        <LoadingOverlay 
          text="Saving recipes..." 
          subtext="This will just take a moment"
          type="dots"
        />
      )}

      <ConnectionStatus />

      {/* Background Generation Indicator */}
      {isGeneratingInBackground && (
        <BackgroundIndicator>
          <span>🚀 Generating recipes in the background...</span>
        </BackgroundIndicator>
      )}
    </AppContainer>
  );
}

export default App;
