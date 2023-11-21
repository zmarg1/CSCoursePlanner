import { Row, Col } from "antd";
import { withTranslation } from "react-i18next";
import { SvgIcon } from "../../../common/SvgIcon";
import { ContentBlockProps } from "../types";
import { Fade } from "react-awesome-reveal";
import {
  LeftContentSection,
  Content,
  ContentWrapper,
  ServiceWrapper,
  MinTitle,
  MinPara,
} from "./styles";
import { useNavigate } from "react-router-dom";
import {Button} from "../../../common/Button";

const scrollTo = (id: string) => {
  const element = document.getElementById(id) as HTMLDivElement;
  element.scrollIntoView({
    behavior: "smooth",
  });
}


const LeftContentBlock = ({
  icon,
  title,
  content,
  section,
  t,
  id,
}: ContentBlockProps) => {
  const navigate = useNavigate(); // useNavigate must be called within the component

  const handleNavigate = (buttonLabel: string) => {
    console.log(`Button clicked: ${buttonLabel}`); // For debugging

    if (buttonLabel === 'Course Plans') {
      console.log('Navigating to /user/plan/make-plan'); // For debugging
      navigate('/user/plan/make-plan');
    } else {
      console.log('Scrolling to about'); // For debugging
      scrollTo("about"); // scrollTo should be defined or handled here
    }
  };

  return (
    <LeftContentSection>
      <Fade direction="right">
        <Row justify="space-between" align="middle" id={id}>
          <Col lg={11} md={11} sm={12} xs={24}>
            <SvgIcon src={icon} width="100%" height="100%" />
          </Col>
          <Col lg={11} md={11} sm={11} xs={24}>
            <ContentWrapper>
              <h6>{t(title)}</h6>
              <Content>{t(content)}</Content>
              <ServiceWrapper>
                <Row justify="space-between">
                  {typeof section === "object" &&
                    section.map((item: any, id: number) => {
                      return (
                        <Col key={id} span={11}>
                          <SvgIcon src={item.icon} width="60px" height="60px" />
                          <MinTitle>{t(item.title)}</MinTitle>
                          <MinPara>{t(item.content)}</MinPara>
                        </Col>
                      );
                    })}
                </Row>
              </ServiceWrapper>
              <Button onClick={() => handleNavigate('Course Plans')}>
                {t('Course Plans')}
              </Button>
            </ContentWrapper>
          </Col>
        </Row>
      </Fade>
    </LeftContentSection>
  );
};

export default withTranslation()(LeftContentBlock);
