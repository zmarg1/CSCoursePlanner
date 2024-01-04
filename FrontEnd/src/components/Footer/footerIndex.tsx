import { Row, Col } from "antd";
import { withTranslation } from "react-i18next";
import { SvgIcon } from "../../common/SvgIcon/svgIcon";
import Container from "../../common/Container/customContainer";
import { useNavigate } from 'react-router-dom';

import i18n from "i18next";
import {
  FooterSection,
  Title,
  NavLink,
  Extra,
  LogoContainer,
  Para,
  Large,
  Empty,
  FooterContainer,
  Language,
  Label,
  LanguageSwitch,
  LanguageSwitchContainer,
} from "./styles";

interface SocialLinkProps {
  href: string;
  src: string;
}

const Footer = ({ t }: any) => {
  const navigate = useNavigate();
  
  const handleChange = (language: string) => {
    i18n.changeLanguage(language);
  };

  const SocialLink = ({ href, src }: SocialLinkProps) => {
    return (
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        key={src}
        aria-label={src}
      >
        <SvgIcon src={src} width="25px" height="25px" />
      </a>
    );
  };

  const handleClassInfoClick = (): void => {
    navigate('/home');
    setTimeout(() => {
      scrollToSection('about');
    }, 0);
  };

  const handleContactClick = (): void => {
    navigate('/home');
    setTimeout(() => {
      scrollToSection('contact');
    }, 0);
  };
  
  const scrollToSection = (sectionId: string): void => {
    const section = document.getElementById(sectionId);
    if (section) {
      section.scrollIntoView({ behavior: 'smooth' });
    }
  };
  
  const handleLogoClick = (): void => {
    navigate('/home');
    window.scrollTo(0, 0);
  };


  return (
    <>
    
      <FooterSection>
        <Container>
          <Row justify="space-between">
            <Col lg={10} md={10} sm={12} xs={12}>
              <Language>{t("Contact")}</Language>
              <Large onClick={handleContactClick}>
                {t("Tell us everything")}
              </Large>
              <Para>
                {t(`Do you have any questions? Feel free to send us an email at planumbc@gmail.com`)}
              </Para>
            </Col>
            <Col lg={8} md={8} sm={12} xs={12}>
              <Title>{t("Sources")}</Title>
              <Large onClick={handleClassInfoClick}>
                {t("Class Information")}
              </Large>
              <Large onClick={handleClassInfoClick}>
                {t("Partners")}
              </Large>
            </Col>
          </Row>
          <Row justify="space-between">
            <Col lg={10} md={10} sm={12} xs={12}>
              <Empty />
              <Language>{t("Address")}</Language>
              <Para>1000 Hilltop Circle</Para>
              <Para>Catonsville MD</Para>
              <Para>United States</Para>
            </Col>
            {/*
              <Col lg={8} md={6} sm={12} xs={12}>
              <Label htmlFor="select-lang">{t("Language")}</Label>
              <LanguageSwitchContainer>
                <LanguageSwitch onClick={() => handleChange("en")}>
                  <SvgIcon
                    src="united-states.svg"
                    aria-label="homepage"
                    width="30px"
                    height="30px"
                  />
                </LanguageSwitch>
                <LanguageSwitch onClick={() => handleChange("es")}>
                  <SvgIcon
                    src="spain.svg"
                    aria-label="homepage"
                    width="30px"
                    height="30px"
                  />
                </LanguageSwitch>
              </LanguageSwitchContainer>
            </Col>
            */}
          </Row>
        </Container>
      </FooterSection>
      <Extra>
        <Container border={true}>
          <Row
            justify="space-between"
            align="middle"
            style={{ paddingTop: "3rem" }}
          >
            <a onClick={handleLogoClick} style={{ cursor: 'pointer' }}>
              <LogoContainer>
                <SvgIcon
                  src="logo.svg"
                  aria-label="homepage"
                  width="141px"
                  height="64px"
                />
              </LogoContainer>
            </a>
            <FooterContainer>
              <SocialLink
                href="https://github.com/zmarg1/CSCoursePlanner/"
                src="github.svg"
              />
              <SocialLink
                href="https://twitter.com/umbccsee"
                src="twitter.svg"
              />
              {/*
              <SocialLink
                href="https://www.linkedin.com/"
                src="linkedin.svg"
              />
              */}
              <a href="https://www.buymeacoffee.com/planumbc.vercel.app">
                <img
                  src="https://img.buymeacoffee.com/button-api/?text=Buy us some coffee!&emoji=☕&slug=planUMBC&button_colour=fdb515&font_colour=ffffff&font_family=Lato&outline_colour=000000&coffee_colour=FFDD00"
                  alt="Buy us some coffee"
                />
              </a>
            </FooterContainer>
          </Row>
        </Container>
      </Extra>
    </>
  );
};

export default withTranslation()(Footer);
