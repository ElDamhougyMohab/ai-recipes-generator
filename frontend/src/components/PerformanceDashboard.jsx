import React from 'react';
import styled from 'styled-components';

const DashboardContainer = styled.div`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  border-radius: 12px;
  margin: 20px 0;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
`;

const DashboardTitle = styled.h3`
  margin: 0 0 15px 0;
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 15px;
  margin-top: 15px;
`;

const StatCard = styled.div`
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 15px;
  text-align: center;
  backdrop-filter: blur(10px);
`;

const StatValue = styled.div`
  font-size: 1.8rem;
  font-weight: bold;
  margin-bottom: 5px;
`;

const StatLabel = styled.div`
  font-size: 12px;
  opacity: 0.8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const ComparisonText = styled.div`
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  padding: 10px;
  margin-top: 15px;
  font-size: 14px;
  text-align: center;
`;

const AsyncBadge = styled.span`
  background: rgba(255, 255, 255, 0.2);
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
`;

export const PerformanceDashboard = ({ metrics, isVisible }) => {
  if (!isVisible || !metrics) return null;

  const estimatedSyncTime = metrics.recipeCount * 2000; // Estimated 2s per recipe without async
  const timeSaved = estimatedSyncTime - metrics.totalTime;
  const efficiencyGain = ((timeSaved / estimatedSyncTime) * 100).toFixed(1);

  return (
    <DashboardContainer>
      <DashboardTitle>
        ⚡ Async Performance Dashboard <AsyncBadge>REAL-TIME</AsyncBadge>
      </DashboardTitle>
      
      <StatsGrid>
        <StatCard>
          <StatValue>{metrics.recipeCount}</StatValue>
          <StatLabel>Recipes Generated</StatLabel>
        </StatCard>
        
        <StatCard>
          <StatValue>{(metrics.totalTime / 1000).toFixed(1)}s</StatValue>
          <StatLabel>Actual Time</StatLabel>
        </StatCard>
        
        <StatCard>
          <StatValue>{(estimatedSyncTime / 1000).toFixed(1)}s</StatValue>
          <StatLabel>Sync Time Would Be</StatLabel>
        </StatCard>
        
        <StatCard>
          <StatValue>{(timeSaved / 1000).toFixed(1)}s</StatValue>
          <StatLabel>Time Saved</StatLabel>
        </StatCard>
        
        <StatCard>
          <StatValue>{efficiencyGain}%</StatValue>
          <StatLabel>Faster</StatLabel>
        </StatCard>
        
        <StatCard>
          <StatValue>{metrics.avgTimePerRecipe}ms</StatValue>
          <StatLabel>Avg per Recipe</StatLabel>
        </StatCard>
      </StatsGrid>
      
      <ComparisonText>
        🚀 <strong>Async Processing:</strong> Generated {metrics.recipeCount} recipes in {(metrics.totalTime / 1000).toFixed(1)}s 
        vs {(estimatedSyncTime / 1000).toFixed(1)}s with traditional sequential processing 
        ({efficiencyGain}% performance improvement!)
      </ComparisonText>
    </DashboardContainer>
  );
};

export default PerformanceDashboard;
