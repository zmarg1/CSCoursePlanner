// App.tsx
import React from 'react';
import { BrowserRouter } from "react-router-dom";
import { ClerkProvider, SignedIn, SignedOut } from '@clerk/clerk-react';
import "antd/dist/antd.css";
import Router from "./router/router";
import i18n from "./translation";
import { I18nextProvider } from 'react-i18next';
import { dark } from '@clerk/themes';
import UserHandler from './UserUtils/UserHandler'; // Import UserHandler

const clerkPubKey = process.env.REACT_APP_CLERK_PUBLISHABLE_KEY;

const App: React.FC = () => {
  if (!clerkPubKey) {
    throw new Error("Clerk publishable key is not set in environment variables.");
  }

  return (
    <ClerkProvider appearance={{ baseTheme: dark }} publishableKey={clerkPubKey}>
      <BrowserRouter>
        <I18nextProvider i18n={i18n}>
          <UserHandler/>
          <SignedIn>
            <Router />
          </SignedIn>
          <SignedOut>
            <Router />
          </SignedOut>
        </I18nextProvider>
      </BrowserRouter>
    </ClerkProvider>
  );
}

export default App;
