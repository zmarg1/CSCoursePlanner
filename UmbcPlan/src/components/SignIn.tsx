// src/components/SignIn.tsx
import React, { useState } from 'react';
import axios from 'axios';

const SignIn: React.FC = () => {
  const [isSignUp, setIsSignUp] = useState(false); // State to toggle between sign-in and sign-up
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState(''); // Needed for sign-up
  const [error, setError] = useState('');

  const handleSignIn = async (event: React.FormEvent) => {
    event.preventDefault();
    // Form data for sign-in
    const formData = new FormData();
    formData.append('email', email);
    formData.append('password', password);

    try {
      const response = await axios({
        method: 'post',
        url: isSignUp ? 'http://localhost:5000/user-signup' : 'http://localhost:5000/user-signin',
        data: formData,
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      // Check response for success or failure
      // Redirect to home or display an error message
      if (response.data === "Successfully signed in user" || response.data === "Successfully signed up user") {
        // Handle successful sign in or sign up
        console.log(response.data);
        // Redirect or manage the user state
      } else {
        setError('Authentication failed.');
      }
    } catch (error) {
      setError('An error occurred. Please try again.');
    }
  };

  // Toggle between Sign In and Sign Up form
  const toggleForm = () => {
    setIsSignUp(!isSignUp);
    setError(''); // Reset errors when toggling
  };

  return (
    <>
      <h2>{isSignUp ? 'Sign Up' : 'Sign In'}</h2>
      <form onSubmit={handleSignIn}>
        <label htmlFor="email">Email:</label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <label htmlFor="password">Password:</label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        {isSignUp && (
          <>
            <label htmlFor="confirmPassword">Confirm Password:</label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
          </>
        )}
        <button type="submit">{isSignUp ? 'Sign Up' : 'Sign In'}</button>
        {error && <p className="error-message">{error}</p>}
      </form>
      <button onClick={toggleForm}>
        {isSignUp ? 'Already have an account? Sign In' : "Don't have an account? Sign Up"}
      </button>
    </>
  );
};

export default SignIn;
