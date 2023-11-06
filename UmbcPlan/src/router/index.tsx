import { lazy, Suspense } from "react";
import { Routes , Route } from "react-router-dom";
import Footer from "../components/Footer";
import Header from "../components/Header";
import routes from "./config";
import { Styles } from "../styles/styles";
import SignIn from "../components/SignIn";

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
        {/* Add the SignIn route directly */}
        <Route path="/user-signin" element={<SignIn />} />
      </Routes>
      <Footer />
    </Suspense>
  );
};

export default Router;
