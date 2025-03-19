import * as React from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './App';
import './styles.css';

// Wait for DOM to be ready
const initializeApp = () => {
  const root = document.getElementById('read-the-room-root');
  if (root) {
    createRoot(root).render(
      <React.StrictMode>
        <App />
      </React.StrictMode>
    );
  }
};

// Check if the element exists, if not, wait for it
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeApp);
} else {
  initializeApp();
} 