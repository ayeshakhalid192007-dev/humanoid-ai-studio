/**
 * Authentication Context for Physical AI Platform
 *
 * Provides authentication state and methods to all components.
 * Uses Better Auth SDK for session management.
 * Includes onboarding profile support.
 */

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  ReactNode,
} from "react";
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';

// Default auth API URL
const DEFAULT_AUTH_API_URL = "http://localhost:3002";

// Function to check API health before making requests
async function checkAuthAPIStatus(authApiUrl: string): Promise<boolean> {
  try {
    const response = await fetch(`${authApiUrl}/health`);
    return response.ok;
  } catch (error) {
    console.warn("Auth API not reachable:", error);
    return false;
  }
}

// User type
export interface User {
  id: string;
  email: string;
  name: string | null;
  image: string | null;
  role: string;
  emailVerified: boolean;
  onboardingCompleted: boolean;
  createdAt: string;
  updatedAt: string;
}

// Session type
export interface Session {
  id: string;
  userId: string;
  token: string;
  expiresAt: string;
}

// User profile (onboarding data)
export interface UserProfile {
  softwareBackground: string;
  hardwareBackground: string;
  roboticsKnowledge: string;
}

// Auth context type
interface AuthContextType {
  user: User | null;
  session: Session | null;
  profile: UserProfile | null;
  isLoading: boolean;
  error: string | null;
  isAuthenticated: boolean;
  needsOnboarding: boolean;
  signUp: (
    email: string,
    password: string,
    name: string
  ) => Promise<{ success: boolean; error?: string }>;
  signUpWithProfile: (
    email: string,
    password: string,
    name: string,
    profile: UserProfile
  ) => Promise<{ success: boolean; error?: string }>;
  signIn: (
    email: string,
    password: string
  ) => Promise<{ success: boolean; error?: string }>;
  signOut: () => Promise<void>;
  refreshSession: () => Promise<void>;
  saveProfile: (
    profile: UserProfile
  ) => Promise<{ success: boolean; error?: string }>;
  fetchProfile: () => Promise<void>;
}

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Auth Provider component
export function AuthProvider({ children }: { children: ReactNode }) {
  const { siteConfig } = useDocusaurusContext();
  const AUTH_API_URL = (siteConfig.customFields?.authApiUrl as string) || DEFAULT_AUTH_API_URL;

  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const isAuthenticated = !!user && !!session;
  const needsOnboarding = isAuthenticated && !user.onboardingCompleted;

  // Fetch current session — Better Auth uses /api/auth/get-session
  const refreshSession = useCallback(async () => {
    try {
      setError(null); // Clear any previous errors

      // Check if API is available first
      const isAPIAvailable = await checkAuthAPIStatus(AUTH_API_URL);
      if (!isAPIAvailable) {
        console.warn("Auth API not available, skipping session refresh");
        return;
      }

      const response = await fetch(`${AUTH_API_URL}/api/auth/get-session`, {
        method: "GET",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const data = await response.json();
        if (data && data.user && data.session) {
          setUser(data.user);
          setSession(data.session);
        } else {
          setUser(null);
          setSession(null);
        }
      } else {
        setUser(null);
        setSession(null);
      }
    } catch (error) {
      console.error("Session refresh error:", error);
      setError(error instanceof Error ? error.message : "Failed to refresh session");
      setUser(null);
      setSession(null);
    } finally {
      setIsLoading(false);
    }
  }, [AUTH_API_URL]);

  // Initialize session on mount
  useEffect(() => {
    refreshSession();
  }, [refreshSession]);

  // Fetch user profile
  const fetchProfile = useCallback(async () => {
    try {
      setError(null); // Clear any previous errors

      // Check if API is available first
      const isAPIAvailable = await checkAuthAPIStatus(AUTH_API_URL);
      if (!isAPIAvailable) {
        console.warn("Auth API not available, skipping profile fetch");
        return;
      }

      const response = await fetch(`${AUTH_API_URL}/api/profile`, {
        method: "GET",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
      });
      if (response.ok) {
        const data = await response.json();
        if (data.profile) {
          setProfile({
            softwareBackground: data.profile.software_background,
            hardwareBackground: data.profile.hardware_background,
            roboticsKnowledge: data.profile.robotics_knowledge,
          });
        }
      } else {
        const errorData = await response.json();
        setError(errorData.error || "Failed to fetch profile");
      }
    } catch (error) {
      console.error("Fetch profile error:", error);
      setError(error instanceof Error ? error.message : "Failed to fetch profile");
    }
  }, [AUTH_API_URL]);

  // Sign up
  const signUp = async (
    email: string,
    password: string,
    name: string
  ): Promise<{ success: boolean; error?: string }> => {
    try {
      setError(null); // Clear any previous errors
      setIsLoading(true);

      // Check if API is available first
      const isAPIAvailable = await checkAuthAPIStatus(AUTH_API_URL);
      if (!isAPIAvailable) {
        throw new Error("Authentication service is currently unavailable. Please try again later.");
      }

      const response = await fetch(`${AUTH_API_URL}/api/auth/sign-up/email`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password, name }),
      });

      const data = await response.json();

      if (response.ok) {
        const userData = data.user || data;
        if (userData.id) {
          setUser({
            id: userData.id,
            email: userData.email,
            name: userData.name || null,
            image: userData.image || null,
            role: userData.role || "student",
            emailVerified: userData.emailVerified || false,
            onboardingCompleted: userData.onboardingCompleted || false,
            createdAt: userData.createdAt || new Date().toISOString(),
            updatedAt: userData.updatedAt || new Date().toISOString(),
          });
          if (data.session) {
            setSession(data.session);
          }
          await refreshSession();
          return { success: true };
        }
        return { success: false, error: "Unexpected response" };
      } else {
        setError(data.message || data.error || "Sign up failed");
        return {
          success: false,
          error: data.message || data.error || "Sign up failed",
        };
      }
    } catch (error) {
      console.error("Sign up error:", error);
      setError(error instanceof Error ? error.message : "Network error. Please try again.");
      return {
        success: false,
        error: error instanceof Error ? error.message : "Network error. Please try again.",
      };
    } finally {
      setIsLoading(false);
    }
  };

  // Sign up with profile — creates account and saves profile in one flow
  const signUpWithProfile = async (
    email: string,
    password: string,
    name: string,
    profileData: UserProfile
  ): Promise<{ success: boolean; error?: string }> => {
    try {
      setError(null); // Clear any previous errors
      setIsLoading(true);

      // Check if API is available first
      const isAPIAvailable = await checkAuthAPIStatus(AUTH_API_URL);
      if (!isAPIAvailable) {
        throw new Error("Authentication service is currently unavailable. Please try again later.");
      }

      // Step 1: Create account
      const signUpResponse = await fetch(
        `${AUTH_API_URL}/api/auth/sign-up/email`,
        {
          method: "POST",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password, name }),
        }
      );

      const signUpData = await signUpResponse.json();

      if (!signUpResponse.ok) {
        const error = signUpData.message || signUpData.error || "Sign up failed";
        setError(error);
        return {
          success: false,
          error: error,
        };
      }

      const userData = signUpData.user || signUpData;
      if (!userData.id) {
        const error = "Unexpected response from server";
        setError(error);
        return { success: false, error: error };
      }

      // Set user/session immediately so profile save has auth context
      if (signUpData.session) {
        setSession(signUpData.session);
      }
      await refreshSession();

      // Step 2: Save profile
      const profileResponse = await fetch(`${AUTH_API_URL}/api/profile`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(profileData),
      });

      const profileResult = await profileResponse.json();

      if (!profileResponse.ok) {
        // Account created but profile failed — user can complete onboarding later
        console.error("Profile save failed after signup:", profileResult.error);
        await refreshSession();
        const partialError = "Account created but profile save failed. You can complete onboarding later.";
        setError(partialError);
        return {
          success: true,
          error: partialError,
        };
      }

      setProfile(profileData);
      setUser((prev) =>
        prev ? { ...prev, onboardingCompleted: true } : prev
      );
      await refreshSession();
      return { success: true };
    } catch (error) {
      console.error("Sign up with profile error:", error);
      const errorMsg = error instanceof Error ? error.message : "Network error. Please try again.";
      setError(errorMsg);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Network error. Please try again.",
      };
    } finally {
      setIsLoading(false);
    }
  };

  // Sign in
  const signIn = async (
    email: string,
    password: string
  ): Promise<{ success: boolean; error?: string }> => {
    try {
      setError(null); // Clear any previous errors
      setIsLoading(true);

      // Check if API is available first
      const isAPIAvailable = await checkAuthAPIStatus(AUTH_API_URL);
      if (!isAPIAvailable) {
        throw new Error("Authentication service is currently unavailable. Please try again later.");
      }

      const response = await fetch(`${AUTH_API_URL}/api/auth/sign-in/email`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        await refreshSession();
        return { success: true };
      } else {
        setError(data.message || data.error || "Invalid credentials");
        return {
          success: false,
          error: data.message || data.error || "Invalid credentials",
        };
      }
    } catch (error) {
      console.error("Sign in error:", error);
      setError(error instanceof Error ? error.message : "Network error. Please try again.");
      return {
        success: false,
        error: error instanceof Error ? error.message : "Network error. Please try again.",
      };
    } finally {
      setIsLoading(false);
    }
  };

  // Sign out
  const signOut = async (): Promise<void> => {
    try {
      setError(null); // Clear any previous errors
      setIsLoading(true);

      // Check if API is available first
      const isAPIAvailable = await checkAuthAPIStatus(AUTH_API_URL);
      if (isAPIAvailable) {
        const response = await fetch(`${AUTH_API_URL}/api/auth/sign-out`, {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
        });

        if (!response.ok) {
          const data = await response.json();
          setError(data.message || data.error || "Sign out failed");
        }
      }
    } catch (error) {
      console.error("Sign out error:", error);
      setError(error instanceof Error ? error.message : "Sign out failed");
    } finally {
      setUser(null);
      setSession(null);
      setProfile(null);
      setIsLoading(false);
    }
  };

  // Save onboarding profile
  const saveProfile = async (
    profileData: UserProfile
  ): Promise<{ success: boolean; error?: string }> => {
    try {
      setError(null); // Clear any previous errors
      setIsLoading(true);

      // Check if API is available first
      const isAPIAvailable = await checkAuthAPIStatus(AUTH_API_URL);
      if (!isAPIAvailable) {
        throw new Error("Authentication service is currently unavailable. Please try again later.");
      }

      const response = await fetch(`${AUTH_API_URL}/api/profile`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(profileData),
      });

      const data = await response.json();

      if (response.ok) {
        setProfile(profileData);
        setUser((prev) =>
          prev ? { ...prev, onboardingCompleted: true } : prev
        );
        return { success: true };
      } else {
        setError(data.error || "Failed to save profile");
        return {
          success: false,
          error: data.error || "Failed to save profile",
        };
      }
    } catch (error) {
      console.error("Save profile error:", error);
      const errorMsg = error instanceof Error ? error.message : "Network error. Please try again.";
      setError(errorMsg);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Network error. Please try again.",
      };
    } finally {
      setIsLoading(false);
    }
  };

  const value: AuthContextType = {
    user,
    session,
    profile,
    isLoading,
    error,
    isAuthenticated,
    needsOnboarding,
    signUp,
    signUpWithProfile,
    signIn,
    signOut,
    refreshSession,
    saveProfile,
    fetchProfile,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// Hook to use auth context
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
