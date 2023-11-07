import React, { } from 'react';
import './App.css';

import {BrowserRouter, Routes, Route} from 'react-router-dom';

import ListCoursePage from "./pages/ListCoursePage";
import CreateCourse from "./pages/CreateCourse";
import EditCourse from './pages/EditCourse';


function App() {
  return (
    <div className = "vh-100 gradient-custom">
    <div className = "container">
      <h1 className = "page-header text-center">Admin Page</h1>

      <BrowserRouter>
        <Routes>
          <Route path = "/" element = {<ListCoursePage />} />
          <Route path = "/create_course" element = {<CreateCourse />} />
          <Route path="course/:id/edit" element={<EditCourse />} />

        </Routes>
      </BrowserRouter>
    </div>
    </div>
  );
}

export default App;
