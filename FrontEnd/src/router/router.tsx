import { lazy, Suspense, useState } from "react";
import { Routes, Route } from "react-router-dom";
import Footer from "../components/Footer/footerIndex";
import Header from "../components/Header/headerIndex";
import routes from "./config";
import { Styles } from "../styles/styles";
import MakePlan from "../pages/MakePlan";
import ViewUserPlan from "../pages/MyPlans/myPlans";
import AdminPage from "../pages/Admin/AdminPage";
import { useUser } from "@clerk/clerk-react";

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
  const { user } = useUser();
  const isAdmin = useState(user?.publicMetadata.admin);

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
      </Routes>
      <Footer />
    </Suspense>
  );
};

export default Router;
