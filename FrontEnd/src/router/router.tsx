import { lazy, Suspense, useEffect, useState, useRef } from "react";
import { Routes, Route, useNavigate  } from "react-router-dom";
import Footer from "../components/Footer/footerIndex";
import Header from "../components/Header/headerIndex";
import routes from "./config";
import { Styles } from "../styles/styles";
import MakePlan from "../pages/MakePlan";
import ViewUserPlan from "../pages/MyPlans/myPlans";
import AdminPage from "../pages/Admin/AdminPage";
import { SignIn, SignUp, useUser, SignedIn, SignedOut } from "@clerk/clerk-react";
import LandingPage from "../pages/LandingPage"; // Import your landing page component
import Home from '../pages/Home/home'; // Adjust the path based on your project structure

import ListCoursePage from "../pages/Course/ListCoursePage";
import CreateCourse from "../pages/Course/CreateCourse";
import EditCourse from "../pages/Course/EditCourse";

import ListSubjectPage from "../pages/Subject/ListSubjectPage";
import CreateSubject from "../pages/Subject/CreateSubject";
import EditSubject from "../pages/Subject/EditSubject";

import ListSemesterPage from "../pages/Semester/ListSemesterPage";
import CreateSemester from "../pages/Semester/CreateSemester";
import EditSemester from "../pages/Semester/EditSemester";

import ListUserPage from "../pages/User/ListUserPage";
import CreateUser from "../pages/User/CreateUser";
import EditUser from "../pages/User/EditUser";

import ListPrereqPage from "../pages/Prereq/ListPrereqPage";
import CreatePrereq from "../pages/Prereq/CreatePrereq";
import EditPrereq from "../pages/Prereq/EditPrereq";

import ListDegreePage from "../pages/Degree/ListDegreePage";
import CreateDegree from "../pages/Degree/CreateDegree";
import EditDegree from "../pages/Degree/EditDegree";

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


  // Define components for routes
  const AdminRoutes = (
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
      <Route path="/admin-page" element={<AdminPage />} />
      <Route path="/admin-courses" element={<ListCoursePage />} />
      <Route path="/admin-courses/addnewcourse" element={<CreateCourse />} />
      <Route path="/admin-courses/course/:id/edit" element={<EditCourse />} />

      <Route path="/admin-subjects" element={<ListSubjectPage />} />
      <Route path="/admin-subjects/addnewsubject" element={<CreateSubject />} />
      <Route path="/admin-subjects/subject/:id/edit" element={<EditSubject />} />

      <Route path="/admin-semesters" element={<ListSemesterPage />} />
      <Route path="/admin-semesters/addnewsemester" element={<CreateSemester />} />
      <Route path="/admin-semesters/semester/:id/edit" element={<EditSemester />} />

      <Route path="/admin-users" element={<ListUserPage />} />
      <Route path="/admin-users/addnewuser" element={<CreateUser />} />
      <Route path="/admin-users/user/:id/edit" element={<EditUser />} />

      <Route path="/admin-prereqs" element={<ListPrereqPage />} />
      <Route path="/admin-prereqs/addnewprereq" element={<CreatePrereq />} />
      <Route path="/admin-prereqs/prereq/:id/edit" element={<EditPrereq />} />

      <Route path="/admin-degrees" element={<ListDegreePage />} />
      <Route path="/admin-degrees/addnewdegree" element={<CreateDegree />} />
      <Route path="/admin-degrees/degree/:id/edit" element={<EditDegree />} />
    </>
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
                {isAdmin && AdminRoutes}
                {AuthenticatedRoutes}
              </Routes>
              <Footer />
            </>
          </SignedIn>
        } />
      </Routes>
    </Suspense>
  );
};

export default Router;