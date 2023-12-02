import { lazy, Suspense } from "react";
import { Routes , Route } from "react-router-dom";
import Footer from "../components/Footer/footerIndex";
import Header from "../components/Header/headerIndex";
import routes from "./config";
import { Styles } from "../styles/styles";
import MakePlan from "../pages/MakePlan";
import ViewUserPlan from "../pages/MyPlan/myPlans";

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
      </Routes>
      <Footer />
    </Suspense>
  );
};

export default Router;
