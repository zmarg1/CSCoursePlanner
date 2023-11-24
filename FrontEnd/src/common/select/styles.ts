import styled from "styled-components";

export const StyledSelect = styled.select<any>`
  font-family: 'Motiva Sans Light', sans-serif;
  background: ${(p) => p.color || "#fdb515"};
  color: ${(p) => (p.color ? "#2E186A" : "#fff")};
  font-size: 1rem;
  font-weight: 600;
  width: 37%;
  border: 2px solid #000000;
  border-radius: 4px;
  padding: 0.05 rem; // Adjusted for a select dropdown
  cursor: pointer;
  transition: all 0.3s ease-in-out;
  box-shadow: 0 16px 30px rgb(23 31 114 / 20%);
  appearance: none; // Removes native OS dropdown styling
  position: relative;

  &:hover,
  &:focus {
    color: #fff;
    border: 2px solid #000000;
    background-color: #636466;
  }

  &:focus {
    outline: none;
    box-shadow: 0 0 0 2px #2e186a;
  }
`;

// If you want a dropdown arrow, you might need an additional wrapper around the select or pseudo-elements.
