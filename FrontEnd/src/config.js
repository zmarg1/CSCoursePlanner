// Config.js
const Config = {
    backendURL: process.env.REACT_APP_BACKEND_URL || 'http://localhost:5000', // Fallback to localhost if the env var is not set
    // ... any other config variables
  };
  
  export default Config;