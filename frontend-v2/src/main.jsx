import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import analytics from './analytics';
import './styles.css';

// Pre-init analytics — sets session id, retries failed events before React mounts
analytics.init({ debug: import.meta.env.DEV });

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
