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
                  <Nav.Link href="/courses">Courses</Nav.Link>
                  <Nav.Link href="/subjects">Subjects</Nav.Link>
                  <Nav.Link href="/prereqs">Prereqs</Nav.Link>
                  <Nav.Link href="/semesters">Semesters</Nav.Link>
                  <Nav.Link href="/users">Users</Nav.Link>
                  <Nav.Link href="/plans">Plans</Nav.Link>

                </Nav>
              </Container>
            </Navbar>
            <br></br>

            <BrowserRouter>
              <Routes>
                <Route path = "/courses" element = {<ListCoursePage />} />
                <Route path = "/courses/addnewcourse" element = {<CreateCourse />} />
                <Route path ="/courses/course/:id/edit" element={<EditCourse />} />

              </Routes>
            </BrowserRouter>
          </div>
        </div>
  );
}

export default App;
