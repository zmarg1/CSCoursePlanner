import { withTranslation } from "react-i18next";
import { Container, StyledInput } from "./customInputStyles";
import { Label } from "../TextArea/textAreaStyles";
import { InputProps } from "../types";

const Input = ({ name, placeholder, onChange, t }: InputProps) => (
  <Container>
    <Label htmlFor={name}>{t(name)}</Label>
    <StyledInput
      placeholder={t(placeholder)}
      name={name}
      id={name}
      onChange={onChange}
    />
  </Container>
);

export default withTranslation()(Input);
