import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { apiUtils } from '../services/api';

const StatusContainer = styled.div`
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  padding: 10px 15px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
  ${props => props.status === 'connected' ? `
    background: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
  ` : `
    background: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
  `}
`;

const StatusIndicator = styled.div`
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 8px;
  ${props => props.status === 'connected' ? `
    background: #28a745;
  ` : `
    background: #dc3545;
  `}
`;

function ConnectionStatus() {
  const [status, setStatus] = useState('checking');
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const checkConnection = async () => {
      try {
        const isHealthy = await apiUtils.checkBackendHealth();
        const newStatus = isHealthy ? 'connected' : 'disconnected';
        
        if (newStatus !== status) {
          setStatus(newStatus);
          setIsVisible(true);
          
          // Auto-hide after 3 seconds if connected
          if (newStatus === 'connected') {
            setTimeout(() => setIsVisible(false), 3000);
          }
        }
      } catch (error) {
        setStatus('disconnected');
        setIsVisible(true);
      }
    };

    // Check immediately
    checkConnection();

    // Check every 30 seconds
    const interval = setInterval(checkConnection, 30000);

    return () => clearInterval(interval);
  }, [status]);

  // Show warning for disconnected state or success message briefly
  if (!isVisible || status === 'checking') {
    return null;
  }

  return (
    <StatusContainer status={status}>
      <StatusIndicator status={status} />
      {status === 'connected' ? 'Connected to server' : 'Server connection lost'}
    </StatusContainer>
  );
}

export default ConnectionStatus;
