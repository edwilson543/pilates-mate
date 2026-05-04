"use client";

import React, { createContext, useContext, useEffect, useState } from "react";

import {
  loginAuthTokenPost,
  refreshAccessTokenAuthTokenRefreshPost,
} from "./apiClient/sdk.gen";
import {
  clearTokens,
  getAccessToken,
  getRefreshToken,
  isTokenExpired,
  setTokens,
} from "./auth";

type AuthContextValue = {
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function initialise() {
      const accessToken = getAccessToken();

      if (!accessToken) {
        setIsAuthenticated(false);
        setIsLoading(false);
        return;
      }

      if (!isTokenExpired(accessToken)) {
        setIsAuthenticated(true);
        setIsLoading(false);
        return;
      }

      const refreshToken = getRefreshToken();
      if (!refreshToken || isTokenExpired(refreshToken)) {
        clearTokens();
        setIsAuthenticated(false);
        setIsLoading(false);
        return;
      }

      try {
        const response = await refreshAccessTokenAuthTokenRefreshPost({
          body: { refresh_token: refreshToken },
          throwOnError: true,
        });
        setTokens(response.data.access_token, response.data.refresh_token);
        setIsAuthenticated(true);
      } catch {
        clearTokens();
        setIsAuthenticated(false);
      } finally {
        setIsLoading(false);
      }
    }

    initialise();
  }, []);

  async function login(email: string, password: string): Promise<void> {
    const response = await loginAuthTokenPost({
      body: { username: email, password },
      throwOnError: true,
    });
    setTokens(response.data.access_token, response.data.refresh_token);
    setIsAuthenticated(true);
  }

  function logout(): void {
    clearTokens();
    setIsAuthenticated(false);
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
