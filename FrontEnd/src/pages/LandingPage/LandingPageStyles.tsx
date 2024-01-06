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

export const WelcomeText = styled("h1")`
  margin-bottom: 0px;
  font-size: 3rem;
`;

export const DescriptionText = styled("h1")`
  margin-bottom: 0px;
  font-size: 2rem;
`;

export const ButtonGroup = styled.div`
  display: flex;
  justify-content: center;
`;

export const StyledButton = styled("button")<any>`
  margin: 10px;
  background: #ffffff; // White background
  color: #000000; // Black text
  font-size: 1.5rem;
  font-weight: 700;
  width: 180px; // Fixed width
  border: 2px solid #000000;
  border-radius: 4px;
  padding: 13px 0;
  cursor: pointer;
  margin-top: 0.625rem;
  transition: all 0.3s ease-in-out;
  box-shadow: 0 16px 30px rgb(23 31 114 / 20%);
  text-align: center; // Center the text
  white-space: nowrap; // Prevent text wrapping
  overflow: hidden; // Hide overflowed text
  text-overflow: ellipsis; // Add ellipsis if text is too long

  &:hover,
  &:active,
  &:focus {
    color: #fff; // White text on hover
    border: 2px solid #000000;
    background-color: #636466; // Dark background on hover
  }
`;