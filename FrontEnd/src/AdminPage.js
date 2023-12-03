import Container from './common/Container/customContainer';
import { Nav } from 'react-bootstrap';
import Navbar from 'react-bootstrap/Navbar';


function AdminPage() {
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
                  <Nav.Link href="/users">Users</Nav.Link>
                  <Nav.Link href="/degrees">Degrees</Nav.Link>

                  <Nav.Link href="/plans">Plans</Nav.Link>
                  <Nav.Link href="/prereqs">Prereqs</Nav.Link>
                  <Nav.Link href="/courses_offered">Courses_Offered</Nav.Link>
                  
                  <Nav.Link href="/taken">Taken</Nav.Link>
                </Nav>
              </Container>
            </Navbar>
            <br></br>
          </div>
        </div>
  );
}

export default AdminPage;