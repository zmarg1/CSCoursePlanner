import { lazy, Suspense } from "react";
import { Routes, Route } from "react-router-dom";
import Footer from "../components/Footer/footerIndex";
import Header from "../components/Header/headerIndex";
import routes from "./config";
import { Styles } from "../styles/styles";
import MakePlan from "../pages/MakePlan";
import ViewUserPlan from "../pages/MyPlans/myPlans";
import AdminPage from "../AdminPage";

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
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Styles />
      <Header />
      <Routes>
        {routes.map((routeItem) => {
          // Dynamically create the JSX element for the lazy component
          const Component = lazy(() => import(`../pages/${routeItem.component}`));
          return (
            <Route
              key={routeItem.key} // Make sure to use a unique key for each route
              path={routeItem.path}
              element={<Component />} // Use the 'element' prop for JSX elements
            />
          );
        })}
        <Route path="/user/plan/make-plan" element={<MakePlan />} />
        <Route path="/user/plan/view-plan/:userEmail" element={<ViewUserPlan />} />
        <Route path="/admin-page" element={<AdminPage />} />
        <Route path="/courses" element={<ListCoursePage />} />
        <Route path="/courses/addnewcourse" element={<CreateCourse />} />
        <Route path="/courses/course/:id/edit" element={<EditCourse />} />

        <Route path="/subjects" element={<ListSubjectPage />} />
        <Route path="/subjects/addnewsubject" element={<CreateSubject />} />
        <Route path="/subjects/subject/:id/edit" element={<EditSubject />} />

        <Route path="/semesters" element={<ListSemesterPage />} />
        <Route path="/semesters/addnewsemester" element={<CreateSemester />} />
        <Route path="/semesters/semester/:id/edit" element={<EditSemester />} />

        <Route path="/users" element={<ListUserPage />} />
        <Route path="/users/addnewuser" element={<CreateUser />} />
        <Route path="/users/user/:id/edit" element={<EditUser />} />

        <Route path="/prereqs" element={<ListPrereqPage />} />
        <Route path="/prereqs/addnewprereq" element={<CreatePrereq />} />
        <Route path="/prereqs/prereq/:id/edit" element={<EditPrereq />} />

        <Route path="/degrees" element={<ListDegreePage />} />
        <Route path="/degrees/addnewdegree" element={<CreateDegree />} />
        <Route path="/degrees/degree/:id/edit" element={<EditDegree />} />
      </Routes>
      <Footer />
    </Suspense>
  );
};

export default Router;
