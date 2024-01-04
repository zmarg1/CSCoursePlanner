import { lazy, Suspense, useEffect, useState, useRef } from "react";
import { Routes, Route, useNavigate  } from "react-router-dom";
import Footer from "../components/Footer/footerIndex";
import Header from "../components/Header/headerIndex";
import routes from "./config";
import { Styles } from "../styles/styles";
import MakePlan from "../pages/MakePlan";
import ViewUserPlan from "../pages/MyPlans/myPlans";

import { SignIn, SignUp, useUser, SignedIn, SignedOut } from "@clerk/clerk-react";
import LandingPage from "../pages/LandingPage/LandingPage";
import Home from '../pages/Home/home';

import AdminPage from "../pages/Admin/AdminPage";
import ListCoursePage from "../pages/Admin/Course/ListCoursePage";
import CreateCourse from "../pages/Admin/Course/CreateCourse";
import EditCourse from "../pages/Admin/Course/EditCourse";

import ListSubjectPage from "../pages/Admin/Subject/ListSubjectPage";
import CreateSubject from "../pages/Admin/Subject/CreateSubject";
import EditSubject from "../pages/Admin/Subject/EditSubject";

import ListSemesterPage from "../pages/Admin/Semester/ListSemesterPage";
import CreateSemester from "../pages/Admin/Semester/CreateSemester";
import EditSemester from "../pages/Admin/Semester/EditSemester";

import ListUserPage from "../pages/Admin/User/ListUserPage";
import CreateUser from "../pages/Admin/User/CreateUser";
import EditUser from "../pages/Admin/User/EditUser";

import ListPrereqPage from "../pages/Admin/Prereq/ListPrereqPage";
import CreatePrereq from "../pages/Admin/Prereq/CreatePrereq";
import EditPrereq from "../pages/Admin/Prereq/EditPrereq";

import ListDegreePage from "../pages/Admin/Degree/ListDegreePage";
import CreateDegree from "../pages/Admin/Degree/CreateDegree";
import EditDegree from "../pages/Admin/Degree/EditDegree";

const Router = () => {
  const { isSignedIn, user } = useUser();
  const navigate = useNavigate();
  const [isAdmin, setIsAdmin] = useState(false);
  const initialLogin = useRef(true);

 

  useEffect(() => {
    if (isSignedIn && initialLogin.current) {
      setIsAdmin(!!user?.publicMetadata?.admin);
      navigate('/home');
      initialLogin.current = false; // Ensures this logic runs only once
    }
  }, [isSignedIn, user, navigate]);


  type AdminRouteProps = {
    children: React.ReactNode;
  };
  
  const AdminRoute: React.FC<AdminRouteProps> = ({ children }) => {
    const { user } = useUser();
    const navigate = useNavigate();
    
    const isAdmin = user && user.publicMetadata && user.publicMetadata.admin;
  
    useEffect(() => {
      if (!isAdmin) {
        navigate('/home'); // Redirect non-admin users
      }
    }, [isAdmin, navigate]);
    
    return isAdmin ? <>{children}</> : null;
    };
  
  // Admin specific routes, isolated from the main layout
  const AdminRoutes = (
      <Route path="/admin-page/*" element={<AdminRoute><AdminPage /></AdminRoute>}>
          <Route index element={<AdminPage />} />
          <Route path="admin-courses" element={<ListCoursePage />} />
          <Route path="admin-courses/addnewcourse" element={<CreateCourse />} />
          <Route path="admin-courses/course/:id/edit" element={<EditCourse />} />

          <Route path="admin-subjects" element={<ListSubjectPage />} />
          <Route path="admin-subjects/addnewsubject" element={<CreateSubject />} />
          <Route path="admin-subjects/subject/:id/edit" element={<EditSubject />} />

          <Route path="admin-semesters" element={<ListSemesterPage />} />
          <Route path="admin-semesters/addnewsemester" element={<CreateSemester />} />
          <Route path="admin-semesters/semester/:id/edit" element={<EditSemester />} />

          <Route path="admin-users" element={<ListUserPage />} />
          <Route path="admin-users/addnewuser" element={<CreateUser />} />
          <Route path="admin-users/user/:id/edit" element={<EditUser />} />

          <Route path="admin-prereqs" element={<ListPrereqPage />} />
          <Route path="admin-prereqs/addnewprereq" element={<CreatePrereq />} />
          <Route path="admin-prereqs/prereq/:id/edit" element={<EditPrereq />} />

          <Route path="admin-degrees" element={<ListDegreePage />} />
          <Route path="admin-degrees/addnewdegree" element={<CreateDegree />} />
          <Route path="admin-degrees/degree/:id/edit" element={<EditDegree />} />
    </Route>
  );


  // Components for your authenticated routes
  const AuthenticatedRoutes = (
    <>
      {routes.map((routeItem) => {
        const Component = lazy(() => import(`../pages/${routeItem.component}`));
        return (
          <Route
            key={routeItem.key}
            path={routeItem.path}
            element={<Component />}
          />
        );
      })}
      <Route path="/home" element={<Home />} />
      <Route path="/user/plan/make-plan" element={<MakePlan />} />
      <Route path="/user/plan/view-plan/:userEmail" element={<ViewUserPlan />} />
    </>
  );
  
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Routes>
        <Route path="/" element={<SignedOut><LandingPage /></SignedOut>} />
        <Route path="/sign-in" element={<SignedOut><SignIn /></SignedOut>} />
        <Route path="/sign-up" element={<SignedOut><SignUp /></SignedOut>} />
        
        <Route path="*" element={
          <SignedIn>
            <>
              <Styles />
              <Header />
              <Routes>
                {AuthenticatedRoutes}
              </Routes>
              <Footer />
            </>
          </SignedIn>
        } />
        
        {/* Admin Routes - Isolated from Main Layout */}
        {AdminRoutes}
      </Routes>
    </Suspense>
  );
};

export default Router;