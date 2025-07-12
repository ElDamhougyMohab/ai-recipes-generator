import React from 'react';
import styled, { keyframes } from 'styled-components';

// Spinning animation
const spin = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

// Pulse animation
const pulse = keyframes`
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
`;

// Bounce animation
const bounce = keyframes`
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
`;

// Wave animation
const wave = keyframes`
  0%, 60%, 100% {
    transform: initial;
  }
  30% {
    transform: translateY(-15px);
  }
`;

// Basic spinner
const SpinnerContainer = styled.div`
  display: inline-flex;
  align-items: center;
  gap: 8px;
`;

const Spinner = styled.div`
  width: ${props => props.size || '20px'};
  height: ${props => props.size || '20px'};
  border: 3px solid ${props => props.color || '#f3f3f3'};
  border-radius: 50%;
  border-top-color: ${props => props.accent || '#667eea'};
  animation: ${spin} 1s ease-in-out infinite;
`;

// Dots loader
const DotsContainer = styled.div`
  display: inline-flex;
  gap: 4px;
  align-items: center;
`;

const Dot = styled.div`
  width: 8px;
  height: 8px;
  background: ${props => props.color || '#667eea'};
  border-radius: 50%;
  animation: ${bounce} 1.4s ease-in-out infinite;
  animation-delay: ${props => props.delay || '0s'};
`;

// Wave loader
const WaveContainer = styled.div`
  display: inline-flex;
  gap: 2px;
  align-items: center;
`;

const WaveBar = styled.div`
  width: 3px;
  height: 20px;
  background: ${props => props.color || '#667eea'};
  border-radius: 2px;
  animation: ${wave} 1.2s ease-in-out infinite;
  animation-delay: ${props => props.delay || '0s'};
`;

// Loading overlay
const OverlayContainer = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(3px);
`;

const OverlayContent = styled.div`
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  text-align: center;
  min-width: 200px;
`;

const OverlayText = styled.div`
  margin-top: 15px;
  color: #333;
  font-size: 16px;
  font-weight: 500;
`;

const OverlaySubtext = styled.div`
  margin-top: 5px;
  color: #666;
  font-size: 14px;
`;

// Inline loader
const InlineContainer = styled.div`
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: ${props => props.color || '#666'};
  font-size: ${props => props.fontSize || '14px'};
`;

// Card skeleton loader
const SkeletonCard = styled.div`
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  animation: ${pulse} 1.5s ease-in-out infinite;
`;

const SkeletonLine = styled.div`
  height: ${props => props.height || '16px'};
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  border-radius: 4px;
  margin-bottom: ${props => props.marginBottom || '10px'};
  width: ${props => props.width || '100%'};
  animation: ${pulse} 1.5s ease-in-out infinite;
  animation-delay: ${props => props.delay || '0s'};
`;

// Loading components
export const LoadingSpinner = ({ size, color, accent, text, ...props }) => (
  <SpinnerContainer {...props}>
    <Spinner size={size} color={color} accent={accent} />
    {text && <span>{text}</span>}
  </SpinnerContainer>
);

export const LoadingDots = ({ color, text, ...props }) => (
  <DotsContainer {...props}>
    <Dot color={color} delay="0s" />
    <Dot color={color} delay="0.2s" />
    <Dot color={color} delay="0.4s" />
    {text && <span style={{ marginLeft: '8px' }}>{text}</span>}
  </DotsContainer>
);

export const LoadingWave = ({ color, text, ...props }) => (
  <WaveContainer {...props}>
    <WaveBar color={color} delay="0s" />
    <WaveBar color={color} delay="0.1s" />
    <WaveBar color={color} delay="0.2s" />
    <WaveBar color={color} delay="0.3s" />
    <WaveBar color={color} delay="0.4s" />
    {text && <span style={{ marginLeft: '8px' }}>{text}</span>}
  </WaveContainer>
);

export const LoadingOverlay = ({ text, subtext, type = 'spinner' }) => (
  <OverlayContainer>
    <OverlayContent>
      {type === 'spinner' && <LoadingSpinner size="40px" />}
      {type === 'dots' && <LoadingDots />}
      {type === 'wave' && <LoadingWave />}
      {text && <OverlayText>{text}</OverlayText>}
      {subtext && <OverlaySubtext>{subtext}</OverlaySubtext>}
    </OverlayContent>
  </OverlayContainer>
);

export const InlineLoader = ({ type = 'spinner', text, color, fontSize, ...props }) => (
  <InlineContainer color={color} fontSize={fontSize} {...props}>
    {type === 'spinner' && <LoadingSpinner size="16px" />}
    {type === 'dots' && <LoadingDots />}
    {type === 'wave' && <LoadingWave />}
    {text && <span>{text}</span>}
  </InlineContainer>
);

export const SkeletonLoader = ({ lines = 3, width, height, ...props }) => (
  <SkeletonCard {...props}>
    {Array.from({ length: lines }, (_, index) => (
      <SkeletonLine
        key={index}
        width={index === lines - 1 ? '60%' : width}
        height={height}
        delay={`${index * 0.1}s`}
        marginBottom={index === lines - 1 ? '0' : '10px'}
      />
    ))}
  </SkeletonCard>
);

// LLM-specific loading component
export const LLMLoader = ({ stage, progress, estimatedTime, ...props }) => {
  const stages = {
    'connecting': 'Connecting to AI service...',
    'processing': 'Processing your request...',
    'generating': 'Generating recipes...',
    'formatting': 'Formatting results...',
    'complete': 'Complete!'
  };

  return (
    <LoadingOverlay
      text={stages[stage] || 'Processing...'}
      subtext={estimatedTime ? `Estimated time: ${estimatedTime}` : 'This may take a few seconds'}
      type="wave"
      {...props}
    />
  );
};

const LoadingComponents = {
  LoadingSpinner,
  LoadingDots,
  LoadingWave,
  LoadingOverlay,
  InlineLoader,
  SkeletonLoader,
  LLMLoader
};

export default LoadingComponents;
