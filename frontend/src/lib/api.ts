/**
 * API client for backend communication
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: any
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

/**
 * Generic fetch wrapper with authentication
 * 
 * CRITICAL: credentials: 'include' sends cookies (NextAuth session) with requests
 */
async function fetchWithAuth(
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  }
  
  // Include credentials to send cookies (NextAuth session)
  // This is how the JWT token gets sent to the backend
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
    credentials: 'include', // CRITICAL: This sends cookies with the request
  })
  
  return response
}

/**
 * Parse response and handle errors
 */
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorMessage = `HTTP ${response.status}: ${response.statusText}`
    let errorData
    
    try {
      errorData = await response.json()
      errorMessage = errorData.detail || errorData.message || errorMessage
    } catch {
      // If response is not JSON, use status text
    }
    
    throw new ApiError(errorMessage, response.status, errorData)
  }
  
  // Handle 204 No Content
  if (response.status === 204) {
    return {} as T
  }
  
  return response.json()
}

/**
 * API client methods
 */
export const api = {
  /**
   * GET request
   */
  async get<T>(endpoint: string): Promise<T> {
    const response = await fetchWithAuth(endpoint, {
      method: 'GET',
    })
    return handleResponse<T>(response)
  },

  /**
   * POST request
   */
  async post<T>(endpoint: string, data?: any): Promise<T> {
    const response = await fetchWithAuth(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    })
    return handleResponse<T>(response)
  },

  /**
   * PATCH request
   */
  async patch<T>(endpoint: string, data?: any): Promise<T> {
    const response = await fetchWithAuth(endpoint, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    })
    return handleResponse<T>(response)
  },

  /**
   * DELETE request
   */
  async delete<T = void>(endpoint: string): Promise<T> {
    const response = await fetchWithAuth(endpoint, {
      method: 'DELETE',
    })
    return handleResponse<T>(response)
  },
}

export { ApiError }

