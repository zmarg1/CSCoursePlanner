import Container from '../../common/Container/customContainer';
import { Nav } from 'react-bootstrap';
import Navbar from 'react-bootstrap/Navbar';
import './AdminStyles.css'
import { CustomNavLinkSmall } from '../../components/Header/styles';

export default function AdminPage() {

  return (
    <div className="container">
      <div className="vh-100 gradient-custom">
        <Navbar bg="light" data-bs-theme="light">
          <Container>

            <Nav className="me-auto">
              <CustomNavLinkSmall>
                <Nav.Link href="/admin-courses">Courses</Nav.Link>
              </CustomNavLinkSmall>

              <CustomNavLinkSmall>
                <Nav.Link href="/admin-subjects">Subjects</Nav.Link>
              </CustomNavLinkSmall>

              <CustomNavLinkSmall>
                <Nav.Link href="/admin-semesters">Semesters</Nav.Link>
              </CustomNavLinkSmall>
              
              <CustomNavLinkSmall>
                <Nav.Link href="/admin-users">Users</Nav.Link>
              </CustomNavLinkSmall>

              <CustomNavLinkSmall>
                <Nav.Link href="/admin-degrees">Degrees</Nav.Link>
              </CustomNavLinkSmall>

              <CustomNavLinkSmall>
                <Nav.Link href="/admin-prereqs">Prereqs</Nav.Link>
              </CustomNavLinkSmall>
            </Nav>
          </Container>
        </Navbar>
        <br></br>
      </div>
    </div>
  );
}