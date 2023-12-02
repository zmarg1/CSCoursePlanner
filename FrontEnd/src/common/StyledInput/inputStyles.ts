import styled from "styled-components";

export const StyledInput = styled.input`
  font-family: 'Motiva Sans Light', sans-serif; // This matches your body font
  color: #000000; // Adjust the color as needed
  font-size: 1rem;
  border-radius: 4px;
  border: 2px solid #000000;
  background: rgb(241, 242, 243); // Or any color you want
  padding: 13px 0;
  width: 100%;
  box-sizing: border-box; // So that padding and border don't affect the width
  transition: all 0.3s ease-in-out;
  
  &:focus {
    outline: none;
    box-shadow: 0 0 0 2px #2e186a;
  }

  &::placeholder {
    color: #aaa; // Placeholder color
  }
`;
