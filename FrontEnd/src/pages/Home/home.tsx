import { lazy } from "react";
import IntroContent from "../../content/IntroContent.json";
import MiddleBlockContent from "../../content/MiddleBlockContent.json";
import AboutContent from "../../content/AboutContent.json";
import ContactContent from "../../content/ContactContent.json";
import { useEffect } from "react";
import { useLocation } from "react-router-dom";

const Contact = lazy(() => import("../../components/ContactForm/contactFormIndex"));
const MiddleBlock = lazy(() => import("../../components/MiddleBlock/middleIndex"));
const Container = lazy(() => import("../../common/Container/customContainer"));
const ScrollToTop = lazy(() => import("../../common/ScrollToTop/scrollTop"));
const ContentBlock = lazy(() => import("../../components/ContentBlock"));

const Home = () => {
  const location = useLocation();

  useEffect(() => {
    // Check if the location state has a scrollToId value
    if (location.state?.scrollToId) {
      const elementId = location.state.scrollToId;
      const element = document.getElementById(elementId);
      if (element) {
        // Scroll to the element smoothly
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
  }, [location]);

  return (
    <Container> 
      <ScrollToTop />
      <ContentBlock
        type="right"
        title={IntroContent.title}
        content={IntroContent.text}
        button={IntroContent.button}
        icon="CrowdAI.jpeg"
        id="home"
      />
      <MiddleBlock
        title={MiddleBlockContent.title}
        content={MiddleBlockContent.text}
        button={MiddleBlockContent.button}
        id="plan"
        image="/img/PlanDog.png"
      />
      <ContentBlock
        type="left"
        title={AboutContent.title}
        content={AboutContent.text}
        section={AboutContent.section}
        icon="UMBCRetrieverAI.svg"
        id="about"
      />
      <Contact
        title={ContactContent.title}
        content={ContactContent.text}
        id="contact"
      />
    </Container>
  );
};

export default Home;
