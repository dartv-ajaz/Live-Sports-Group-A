
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error("Could not find root element to mount to");
}

const root = ReactDOM.createRoot(rootElement);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
// In your React Component
const handlePlay = (matchData) => {
    // Check if window.playMatch exists to avoid errors
    if (window.playMatch) {
        window.playMatch(matchData);
    } else {
        console.error("Router function not found");
    }
};