import { Row, Col } from "antd";
import { withTranslation } from "react-i18next";
import { Fade } from "react-awesome-reveal";
import { Button } from "../../common/Button";
import { MiddleBlockSection, Content, ContentWrapper } from "./styles";
import { useNavigate } from "react-router-dom";

interface MiddleBlockProps {
  title: string;
  content: string;
  button: string;
  id: string;
  t: any;
}

const MiddleBlock = ({ title, content, button, id, t }: MiddleBlockProps) => {
  const scrollTo = (id: string) => {
    const element = document.getElementById(id) as HTMLDivElement;
    element.scrollIntoView({
      behavior: "smooth",
    });
  };

  const navigate = useNavigate();
  const handleNavigate = (buttonLabel: string) => {
    console.log(`Button clicked: ${buttonLabel}`); // For debugging
  
    if (buttonLabel === '+') {
      console.log('Navigating to /user/plan/make-plan'); // For debugging
      navigate('/user/plan/make-plan');
    } else {
      console.log('Scrolling to mission'); // For debugging
      scrollTo("about");
    }
  };
  

  return (
    <MiddleBlockSection>
      <Fade direction="left">
        <Row justify="center" align="middle" id={id}>
          <ContentWrapper>
            <Col lg={24} md={24} sm={24} xs={24}>
              <h6>{t(title)}</h6>
              <Content>{t(content)}</Content>
              {button && (
                <Button
                  name="submit"
                  onClick={() => handleNavigate(t(button))}
                >
                  {t(button)}
                </Button>
              )}
            </Col>
          </ContentWrapper>
        </Row>
      </Fade>
    </MiddleBlockSection>
  );
};

export default withTranslation()(MiddleBlock);
