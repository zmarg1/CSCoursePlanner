import { useState } from "react";
import { Row, Col, Drawer } from "antd";
import { useNavigate } from 'react-router-dom';
import { withTranslation } from "react-i18next";
import Container from "../../common/Container";
import { SvgIcon } from "../../common/SvgIcon";
import { SignedIn, SignedOut, useClerk, UserButton } from '@clerk/clerk-react';

import {
  HeaderSection,
  LogoContainer,
  Burger,
  NotHidden,
  Menu,
  CustomNavLinkSmall,
  Label,
  Outline,
  Span,
} from "./styles";

const Header = ({ t }: any) => {
  const [visible, setVisibility] = useState(false);
  const navigate = useNavigate();

  const showDrawer = () => {
    setVisibility(!visible);
  };

  const onClose = () => {
    setVisibility(!visible);
  };

  const handleNavigationClick = (path: string, id?: string) => {
    // Close the drawer if open
    setVisibility(false);
    // Navigate to the path
    navigate(path, {
      state: { scrollToId: id } // Pass along the id to scroll to
    });
  };

  const clerk = useClerk();

  const handleSignInClick = () => {
    clerk.openSignIn();// Navigate to your sign-in route
  };

  const handlePlanClick = () => {
    navigate('/user/plan/make-plan'); // Navigate to your make-plan route
  };

  // const handleAboutClick = () => {
  //   navigate('/'); // Navigate to your sign-in route
  // };

  // const handleContactClick = () => {
  //   navigate('/'); // Navigate to your sign-in route
  // };

  // const scrollTo = (id: string) => {
  //   const element = document.getElementById(id) as HTMLDivElement;
  //   element.scrollIntoView({
  //     behavior: "smooth",
  //   });
  //   setVisibility(false);
  // };

  const MenuItem = () => {
    return (
      <>
        <CustomNavLinkSmall onClick={() => handleNavigationClick('/', 'home')}>
          <Span>{t("Home")}</Span>
        </CustomNavLinkSmall>
        <CustomNavLinkSmall onClick={handlePlanClick}>
          <Span>{t("Plan")}</Span>
        </CustomNavLinkSmall>
        <CustomNavLinkSmall onClick={() => handleNavigationClick('/', 'about')}>
          <Span>{t("About")}</Span>
        </CustomNavLinkSmall>
        <CustomNavLinkSmall onClick={() => handleNavigationClick('/', 'contact')}>
          <Span>{t("Contact")}</Span>
        </CustomNavLinkSmall>
        <SignedOut>
        <CustomNavLinkSmall onClick={handleSignInClick}>
          <Span>{t("Sign In")}</Span>
        </CustomNavLinkSmall>
        </SignedOut>
        <CustomNavLinkSmall>
        <SignedIn>
        <UserButton/>
        </SignedIn>
        </CustomNavLinkSmall>
        
      </>
    );
  };

  return (
    <HeaderSection>
      <Container>
        <Row justify="space-between">
          <NotHidden>
            <MenuItem />
          </NotHidden>
          <LogoContainer to="/" aria-label="homepage">
            <SvgIcon src="logo.svg" width="141px" height="64px" />
          </LogoContainer>
          <Burger onClick={showDrawer}>
            <Outline />
          </Burger>
        </Row>
        <Drawer closable={false} open={visible} onClose={onClose}>
          <Col style={{ marginBottom: "2.5rem" }}>
            <Label onClick={onClose}>
              <Col span={12}>
                <Menu>{t("Menu")}</Menu>
              </Col>
              <Col span={12}>
                <Outline />
              </Col>
            </Label>
          </Col>
          <MenuItem />
        </Drawer>
      </Container>
    </HeaderSection>
  );
};

export default withTranslation()(Header);
