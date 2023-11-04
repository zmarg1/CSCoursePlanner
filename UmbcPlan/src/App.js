import React, { } from 'react';
import './App.css';

import {BrowserRouter, Routes, Route} from 'react-router-dom';

import ListCoursePage from "./pages/ListCoursePage";

function App() {
  return (
    <div className = "vh-100 gradient-custom">
    <div className = "container">
      <h1 className = "page-header text-center">Admin Page</h1>

      <BrowserRouter>
        <Routes>
          <Route path = "/" element = {<ListCoursePage />} />
        </Routes>
      </BrowserRouter>
    </div>
    </div>
  );
}

export default App;
