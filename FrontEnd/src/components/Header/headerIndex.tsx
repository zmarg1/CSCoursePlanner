import React, { useState } from "react";
import { Row, Col, Drawer } from "antd";
import { useNavigate } from 'react-router-dom';
import { withTranslation } from "react-i18next";
import Container from "../../common/Container/customContainer";
import { SvgIcon } from "../../common/SvgIcon/svgIcon";
import { SignedIn, SignedOut, useClerk, UserButton } from '@clerk/clerk-react';
import { useUser } from '@clerk/clerk-react';

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
  const { user } = useUser();
  const [visible, setVisibility] = useState(false);
  const navigate = useNavigate();

  const showDrawer = () => {
    setVisibility(!visible);
  };

  const onClose = () => {
    setVisibility(!visible);
  };

  const handleNavigationClick = (path: string, id?: string) => {
    setVisibility(false);
    navigate(path, { state: { scrollToId: id } });
  };

  const clerk = useClerk();

  //const handleSignInClick = () => {
  //  clerk.openSignIn();
  //};

  const handlePlanClick = () => {
    navigate('/user/plan/make-plan');
  };

  const handleMyPlanClick = () => {
    const userEmail = user?.emailAddresses[0]?.emailAddress;
    navigate(`/user/plan/view-plan/${userEmail}`);
  };

  const handleAdminClick = () => {
    navigate('/admin-page');
  };

  const MenuItem = () => {
    const [isAdmin] = useState(user?.publicMetadata.admin);
    
    return (
      <>
        <CustomNavLinkSmall onClick={handlePlanClick}>
          <Span>{t("Build Plan")}</Span>
        </CustomNavLinkSmall>
        <CustomNavLinkSmall onClick={handleMyPlanClick}>
          <Span>{t("MyPlans")}</Span>
        </CustomNavLinkSmall>
        <CustomNavLinkSmall onClick={() => handleNavigationClick('/home', 'about')}>
          <Span>{t("About")}</Span>
        </CustomNavLinkSmall>
        <CustomNavLinkSmall onClick={() => handleNavigationClick('/home', 'contact')}>
          <Span>{t("Contact")}</Span>
        </CustomNavLinkSmall>

        {/* Disable Admin page temporarily
        {isAdmin && (
          <CustomNavLinkSmall onClick={handleAdminClick}>
            <Span>{t("Admin Page")}</Span>
          </CustomNavLinkSmall>
        )}
        */}
      </>
    );
  };

  return (
    <HeaderSection>
      <Container>
        <Row align="middle" style={{ display: 'flex', justifyContent: 'space-between' }}>
          <Col style={{ flex: 1.3 }}>
            <LogoContainer to="/home" aria-label="homepage">
              <SvgIcon src="logo.svg" width="141px" height="64px" />
            </LogoContainer>
          </Col>

          <Col style={{ display: 'flex', justifyContent: 'center' }}>
            <NotHidden>
              <MenuItem />
            </NotHidden>
          </Col>

          <Col style={{ flex: 1, display: 'flex', justifyContent: 'flex-end' }}>
            {/* 
            <SignedOut>
              <CustomNavLinkSmall onClick={handleSignInClick}>
                <Span>{t("Sign In")}</Span>
              </CustomNavLinkSmall>
            </SignedOut> 
            */}
            <SignedIn>
              <UserButton />
            </SignedIn>
          </Col>
        </Row>

        <Burger onClick={showDrawer}>
          <Outline />
        </Burger>
        {/* </Container> */}

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