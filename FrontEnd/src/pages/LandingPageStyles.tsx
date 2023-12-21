// LandingPageStyles.tsx
import styled from 'styled-components';


export const LandingContainer = styled.div`
  display: flex;
  text-align: center;
  height: 100vh; /* Set the height to 100% of the viewport height */
`;

export const LeftSide = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
`;

export const RightSide = styled.div`
  flex: 1;
  background-color: #fdb515; /* Add the yellow background color */
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
`;

export const LogoContainer = styled.div`
  display: flex;
  align-items: center;
  margin-left: 30px; /* Add margin to the left to adjust the spacing with the "Welcome" text */
`;

export const WelcomeContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin-bottom: 30px; /* Adjust the margin as needed */
`;

export const WelcomeText = styled.h1`
  margin-bottom: 20px;
`;

export const DescriptionText = styled.h1`
  margin-bottom: 30px;
`;

export const Button = styled.button`
  margin: 10px;
  padding: 10px 20px;
  background-color: #0057ff; /* Adjust the color to match your app's theme */
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;

  &:hover {
    opacity: 0.9;
  }
`;

export const ButtonGroup = styled.div`
  display: flex;
  justify-content: center;
`;