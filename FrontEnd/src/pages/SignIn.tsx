import React from 'react';
import { SignIn as ClerkSignIn } from '@clerk/clerk-react';
import styled from 'styled-components';

const StyledSignInContainer = styled.div`
  // Add your custom styles here
`;

const SignIn: React.FC = () => {
  return (
    <StyledSignInContainer>
      <ClerkSignIn />
    </StyledSignInContainer>
  );
};

export default SignIn;
