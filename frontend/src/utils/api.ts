/**
 * API configuration utilities for InvestigatorAI Frontend
 */

/**
 * Get the API base URL from environment variables
 * Falls back to localhost for development
 */
export const getApiUrl = (): string => {
  // In Next.js, environment variables prefixed with NEXT_PUBLIC_ are available in the browser
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  
  // Remove trailing slash if present
  return apiUrl.replace(/\/$/, '');
};

/**
 * Create a full API endpoint URL
 * @param endpoint - The API endpoint path (e.g., '/health', '/investigate/stream')
 * @returns Full URL to the API endpoint
 */
export const createApiUrl = (endpoint: string): string => {
  const baseUrl = getApiUrl();
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${baseUrl}${cleanEndpoint}`;
};

/**
 * Default fetch options for API calls
 */
export const defaultFetchOptions: RequestInit = {
  headers: {
    'Content-Type': 'application/json',
  },
};

/**
 * Enhanced fetch wrapper with error handling
 */
export const apiFetch = async (
  endpoint: string, 
  options: RequestInit = {}
): Promise<Response> => {
  const url = createApiUrl(endpoint);
  const mergedOptions = {
    ...defaultFetchOptions,
    ...options,
    headers: {
      ...defaultFetchOptions.headers,
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, mergedOptions);
    return response;
  } catch (error) {
    console.error(`API call failed for ${endpoint}:`, error);
    throw error;
  }
};
