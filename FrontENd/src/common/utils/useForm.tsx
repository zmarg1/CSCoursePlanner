import { useState, useEffect } from "react";
import { notification } from "antd";
import emailjs from 'emailjs-com';

export const useForm = (validate: any) => {
  const [values, setValues] = useState({});
  const [errors, setErrors] = useState({});
  const [shouldSubmit, setShouldSubmit] = useState(false);

  const reset = () => {
    setValues({}); // Reset to empty or initial state
  };

  const openNotificationWithIcon = () => {
    notification["success"]({
      message: "Success",
      description: "Your message has been sent!",
    });
  };

  const SERVICE_ID = "service_n4v9cug"
  const TEMPLATE_ID = "template_hoea56f"
  const USER_ID = "deTJz0mXvUp85n4qR"


  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setErrors(validate(values));
  
    if (Object.keys(values).length === 3 && Object.values(values).every(value => value)) {
      emailjs.sendForm(SERVICE_ID, TEMPLATE_ID, event.currentTarget, USER_ID)
        .then((result) => {
          console.log(result.text);
          setShouldSubmit(true);
          reset(); // Call the reset function after successful submission
          openNotificationWithIcon(); // Notify the user
        }, (error) => {
          console.log(error.text);
        });
    }
  };

  const resetForm = () => {
    setValues({
      name: '',
      email: '',
      message: ''
    });
    setShouldSubmit(false);
    setErrors({});
  };
  

  useEffect(() => {
    if (shouldSubmit) {
      resetForm();
      setShouldSubmit(false);
    }
  }, [shouldSubmit]);

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    event.persist();
    setValues((values) => ({
      ...values,
      [event.target.name]: event.target.value,
    }));
    setErrors((errors) => ({ ...errors, [event.target.name]: "" }));
  };

  return {
    handleChange,
    handleSubmit,
    values,
    errors,
    reset,
  };
};
