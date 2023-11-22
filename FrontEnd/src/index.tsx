import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './app'; // Import App from app.tsx

const rootElm =  document.getElementById('root');

if (rootElm){
  const root = ReactDOM.createRoot(rootElm);

  root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
}
else{
  console.error('Root element with id "root" not found');
}
