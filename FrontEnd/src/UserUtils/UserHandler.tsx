// UserHandler.tsx
import React, { useEffect } from 'react';
import { useUser } from '@clerk/clerk-react';
import { updateSupabaseUser } from './updateSupabaseUser';

const UserHandler: React.FC = () => {
  const { user } = useUser();

  useEffect(() => {
    if (user) {
      // Get the email address from the Clerk user object
      const email = user.emailAddresses?.[0]?.emailAddress || '';
      updateSupabaseUser(user.id, email);
    }
  }, [user]);

  return null; // This component doesn't render anything visually
};

export default UserHandler;


