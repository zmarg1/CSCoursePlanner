import React, { } from 'react';
import './App.css';

import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';

import {BrowserRouter, Routes, Route} from 'react-router-dom';

import ListCoursePage from "./pages/ListCoursePage";
import CreateCourse from "./pages/CreateCourse";
import EditCourse from './pages/EditCourse';


function App() {
  return (
          <div className = "container">
            <div className = "vh-100 gradient-custom">
            <Navbar bg="light" data-bs-theme="light">
              <Container>
                <Navbar.Brand>Admin</Navbar.Brand>
                <Nav className="me-auto">
                  <Nav.Link href="/">Courses</Nav.Link>
                  <Nav.Link href="/">Subjects</Nav.Link>
                  <Nav.Link href="/">Prereqs</Nav.Link>
                  <Nav.Link href="/">Semesters</Nav.Link>
                  <Nav.Link href="/">Users</Nav.Link>
                  <Nav.Link href="/">Plans</Nav.Link>

                </Nav>
              </Container>
            </Navbar>
            <br></br>

            <BrowserRouter>
              <Routes>
                <Route path = "/" element = {<ListCoursePage />} />
                <Route path = "/create_course" element = {<CreateCourse />} />
                <Route path ="course/:id/edit" element={<EditCourse />} />

              </Routes>
            </BrowserRouter>
          </div>
        </div>
  );
}

export default App;
