import Container from '../../common/Container/customContainer';
import { Nav } from 'react-bootstrap';
import Navbar from 'react-bootstrap/Navbar';
import './AdminStyles.css'
import { CustomNavLinkSmall } from '../../components/Header/styles';
import { Link, Outlet } from 'react-router-dom';

export default function AdminPage() {

  return (
    <div className="container">
      <div className="vh-100 gradient-custom">
        <Navbar bg="light" data-bs-theme="light">
          <Container>

            <Nav className="me-auto">
              <CustomNavLinkSmall>
                <Link to="admin-courses" className="nav-link">Courses</Link>
              </CustomNavLinkSmall>

              <CustomNavLinkSmall>
                <Link to="admin-subjects" className="nav-link">Subjects</Link>
              </CustomNavLinkSmall>

              <CustomNavLinkSmall>
                <Link to="admin-semesters" className="nav-link">Semesters</Link>
              </CustomNavLinkSmall>
              
              <CustomNavLinkSmall>
                <Link to="admin-users" className="nav-link">Users</Link>
              </CustomNavLinkSmall>

              <CustomNavLinkSmall>
                <Link to="admin-degrees" className="nav-link">Degrees</Link>
              </CustomNavLinkSmall>

              <CustomNavLinkSmall>
                <Link to="admin-prereqs" className="nav-link">Prereqs</Link>
              </CustomNavLinkSmall>
            </Nav>
          </Container>
        </Navbar>
        <br></br>
        {/* Outlet to render the content of the selected admin option */}
        <Outlet />
      </div>
    </div>
  );
}