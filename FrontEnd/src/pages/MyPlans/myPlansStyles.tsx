import styled from "styled-components";
import { Styles } from "../../styles/styles";
 
export const GridContainer = styled("div")`
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between; /* Adjust as needed */
  `;
  
export const GridItem = styled("div")`
    flex: 0 1 48%; /* Adjust as needed for the number of items in a row */
    margin-bottom: 20px; /* Adjust as needed */
  `;
  
export const CourseItem = styled("li")`
    display: flex;
    align-items: center;
    margin-bottom: 2%;
    margin-right: 3%;
    width: 100%; /* Ensure full width by default */
  `;
  
export const CourseDetails = styled("div")`
    flex: 0.9;
    margin-right: 2%;
  `;
  
export const ButtonContainer = styled("div")`
    margin-left: 20%;
    width: 40%
  `;
  
export const TermHeading = styled("div")`
align-items: center;
  `;

export const YearHeading = styled("h6")`
  align-items: center;
  margin-top: 1%;
`;