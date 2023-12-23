// LandingPage.tsx
import React from 'react';
//import { useNavigate } from 'react-router-dom';
import { SvgIcon } from "../../common/SvgIcon/svgIcon"

//import { SignedIn, SignedOut, useClerk, UserButton } from '@clerk/clerk-react';
//import { useUser } from '@clerk/clerk-react';

import { useClerk, UserButton } from '@clerk/clerk-react';

import {
  LandingContainer,
  LeftSide,
  RightSide,
  WelcomeText,
  DescriptionText,
  ButtonGroup,
  LogoContainer,
  WelcomeContainer, 
  StyledButton
} from './LandingPageStyles';

const LandingPage = () => {
  //const navigate = useNavigate();

  //const handleSignIn = () => {
    // Navigate to the centered clerk component
    //navigate('/sign-in');
  //};

  //const handleSignUp = () => {
    //navigate('/sign-up');
  //};

  const clerk = useClerk();

  const handleSignInClick = () => {
    clerk.openSignIn();
  };

  const handleSignUpClick = () => {
    clerk.openSignUp();
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
        <DescriptionText>Start Planning</DescriptionText>
        <ButtonGroup>
          <StyledButton onClick={handleSignInClick}>Login</StyledButton>
          <StyledButton onClick={handleSignUpClick}>Sign-Up</StyledButton>
        </ButtonGroup>
      </RightSide>
    </LandingContainer>
  );
};

export default LandingPage;