'use client'
import { Button } from '@/components/ui/button';
import { useState } from 'react';

export default function SignInPage() {

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSignIn = (e) => {
    e.preventDefault();
    // Handle the sign-in logic here
    console.log("Email:", email, "Password:", password);
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="w-full max-w-md p-8 space-y-6 bg-white rounded-lg shadow-md">
        <h2 className="text-2xl font-semibold text-center text-gray-800">Sign In</h2>
        <form className="space-y-4" onSubmit={handleSignIn}>
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">Email address</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-2 mt-1 border rounded-md focus:ring focus:ring-opacity-50 focus:ring-blue-500 focus:outline-none"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-4 py-2 mt-1 border rounded-md focus:ring focus:ring-opacity-50 focus:ring-blue-500 focus:outline-none"
            />
          </div>

          <Button type="submit" className="w-full mt-6">Sign In</Button>
        </form>

        <div className="text-center">
          <p className="text-sm text-gray-600">Don't have an account? <a href="/signup" className="font-medium text-blue-600 hover:underline">Sign up</a></p>
        </div>
      </div>
    </div>
  );
}
