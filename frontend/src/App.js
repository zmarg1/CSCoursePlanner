import React, { } from 'react';
import './App.css';

import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';

import {BrowserRouter, Routes, Route} from 'react-router-dom';

import ListCoursePage from "./pages/Course/ListCoursePage";
import CreateCourse from "./pages/Course/CreateCourse";
import EditCourse from './pages/Course/EditCourse';

import ListSubjectPage from "./pages/Subject/ListSubjectPage";
import CreateSubject from "./pages/Subject/CreateSubject";
import EditSubject from './pages/Subject/EditSubject';

import ListSemesterPage from "./pages/Semester/ListSemesterPage";
import CreateSemester from "./pages/Semester/CreateSemester";
import EditSemester from './pages/Semester/EditSemester';

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
                  <Nav.Link href="/semesters">Semesters</Nav.Link>
                  <Nav.Link href="/prereqs">Prereqs</Nav.Link>
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

                <Route path = "/subjects" element = {<ListSubjectPage />} />
                <Route path = "/subjects/addnewsubject" element = {<CreateSubject />} />
                <Route path ="/subjects/subject/:id/edit" element={<EditSubject />} />

                <Route path = "/semesters" element = {<ListSemesterPage />} />
                <Route path = "/semesters/addnewsemester" element = {<CreateSemester />} />
                <Route path ="/semesters/semester/:id/edit" element={<EditSemester />} />

              </Routes>
            </BrowserRouter>
          </div>
        </div>
  );
}

export default App;
