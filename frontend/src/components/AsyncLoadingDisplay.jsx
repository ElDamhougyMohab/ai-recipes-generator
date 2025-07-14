import React from 'react';
import styled, { keyframes } from 'styled-components';

// Enhanced loading animations
const shimmer = keyframes`
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
`;

const progressPulse = keyframes`
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
`;

const LoadingContainer = styled.div`
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  margin: 20px 0;
  text-align: center;
`;

const StageTitle = styled.h3`
  color: #333;
  margin-bottom: 20px;
  font-size: 1.4rem;
`;

const ProgressBarContainer = styled.div`
  background: #f0f0f0;
  border-radius: 20px;
  height: 8px;
  margin: 20px 0;
  overflow: hidden;
  position: relative;
`;

const ProgressBar = styled.div`
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 20px;
  width: ${props => (props.current / props.total) * 100}%;
  transition: width 0.5s ease;
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
    animation: ${shimmer} 2s infinite;
  }
`;

const ProgressText = styled.div`
  font-size: 14px;
  color: #666;
  margin-top: 10px;
`;

const MetricsContainer = styled.div`
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-top: 20px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
`;

const MetricItem = styled.div`
  text-align: center;
`;

const MetricValue = styled.div`
  font-size: 1.5rem;
  font-weight: bold;
  color: #667eea;
  margin-bottom: 5px;
`;

const MetricLabel = styled.div`
  font-size: 12px;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const AsyncBadge = styled.div`
  display: inline-block;
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  margin-top: 10px;
  animation: ${progressPulse} 2s infinite;
  background-size: 200% 200%;
`;

const StreamingContainer = styled.div`
  margin-top: 30px;
`;

const StreamingTitle = styled.h4`
  color: #333;
  margin-bottom: 15px;
`;

const RecipePreview = styled.div`
  background: white;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  padding: 15px;
  margin: 10px 0;
  text-align: left;
  opacity: 0;
  animation: fadeInUp 0.5s ease forwards;
  animation-delay: ${props => props.delay || '0s'};
  
  @keyframes fadeInUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
`;

const RecipeTitle = styled.h5`
  color: #333;
  margin: 0 0 8px 0;
  font-size: 1.1rem;
`;

const RecipeDesc = styled.p`
  color: #666;
  margin: 0;
  font-size: 14px;
  line-height: 1.4;
`;

export const AsyncLoadingDisplay = ({ 
  stage, 
  progressData, 
  generationMetrics, 
  streamingRecipes = []
}) => {
  const stages = {
    'connecting': { emoji: '🔗', text: 'Connecting to AI service...' },
    'processing': { emoji: '🧠', text: 'Processing your request...' },
    'generating': { emoji: '⚡', text: 'Generating recipes with async AI...' },
    'formatting': { emoji: '✨', text: 'Formatting results...' },
    'complete': { emoji: '🎉', text: 'Generation complete!' }
  };

  const currentStage = stages[stage] || { emoji: '⏳', text: 'Processing...' };

  return (
    <LoadingContainer>
      <StageTitle>
        {currentStage.emoji} {currentStage.text}
      </StageTitle>
      
      {progressData.total > 0 && (
        <>
          <ProgressBarContainer>
            <ProgressBar current={progressData.current} total={progressData.total} />
          </ProgressBarContainer>
          <ProgressText>
            Step {progressData.current} of {progressData.total}: {progressData.stage}
          </ProgressText>
        </>
      )}
      
      <AsyncBadge>
        🚀 Async LLM Processing Active
      </AsyncBadge>
      
      {generationMetrics && (
        <MetricsContainer>
          <MetricItem>
            <MetricValue>{generationMetrics.recipeCount}</MetricValue>
            <MetricLabel>Recipes Generated</MetricLabel>
          </MetricItem>
          <MetricItem>
            <MetricValue>{generationMetrics.totalTime}ms</MetricValue>
            <MetricLabel>Total Time</MetricLabel>
          </MetricItem>
          <MetricItem>
            <MetricValue>{generationMetrics.avgTimePerRecipe}ms</MetricValue>
            <MetricLabel>Avg per Recipe</MetricLabel>
          </MetricItem>
          <MetricItem>
            <MetricValue>{generationMetrics.efficiency}</MetricValue>
            <MetricLabel>Async Efficiency</MetricLabel>
          </MetricItem>
        </MetricsContainer>
      )}
      
      {streamingRecipes.length > 0 && (
        <StreamingContainer>
          <StreamingTitle>🔄 Recipes streaming in real-time:</StreamingTitle>
          {streamingRecipes.map((recipe, index) => (
            <RecipePreview key={recipe.id || index} delay={`${index * 0.2}s`}>
              <RecipeTitle>{recipe.title}</RecipeTitle>
              <RecipeDesc>
                {recipe.description.substring(0, 100)}...
              </RecipeDesc>
            </RecipePreview>
          ))}
        </StreamingContainer>
      )}
    </LoadingContainer>
  );
};

export default AsyncLoadingDisplay;
