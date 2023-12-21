// LandingPage.tsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { SvgIcon } from "../common/SvgIcon/svgIcon"

import {
  LandingContainer,
  LeftSide,
  RightSide,
  WelcomeText,
  DescriptionText,
  Button,
  ButtonGroup,
  LogoContainer,
  WelcomeContainer
} from './LandingPageStyles';

const LandingPage = () => {
  const navigate = useNavigate();

  const handleSignIn = () => {
    // Navigate to the centered clerk component
    navigate('/sign-in');
  };

  const handleSignUp = () => {
    navigate('/sign-up');
  };

  return (
    <LandingContainer>
      <LeftSide>
        <WelcomeContainer>
          <WelcomeText>Welcome to</WelcomeText>
          <LogoContainer>
                <SvgIcon src="logo.svg" width="423px" height="192px" />
          </LogoContainer>
        </WelcomeContainer>
      </LeftSide>
      <RightSide>
        <DescriptionText>Get started</DescriptionText>
        <ButtonGroup>
          <Button onClick={handleSignIn}>Sign In</Button>
          <Button onClick={handleSignUp}>Sign Up</Button>
        </ButtonGroup>
      </RightSide>
    </LandingContainer>
  );
};

export default LandingPage;