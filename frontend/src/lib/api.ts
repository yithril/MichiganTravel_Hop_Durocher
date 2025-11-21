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
 * Type definitions for API responses
 */
export interface TripResponse {
  id: number
  name: string
  user_id: number
  start_location_text?: string | null
  start_latitude?: number | null
  start_longitude?: number | null
  num_days: number
  trip_mode: string
  budget_band: string
  companions?: string | null
  status: string
  created_at: string
  updated_at: string
}

export interface TripStopResponse {
  id: number
  trip_day_id: number
  attraction_id?: number | null
  attraction_name?: string | null
  attraction_type?: string | null
  label?: string | null
  slot: string
  order_index: number
  created_at: string
  updated_at: string
}

export interface TripDayResponse {
  id: number
  trip_id: number
  day_index: number
  base_city_id?: number | null
  base_city_name?: string | null
  notes?: string | null
  stops: TripStopResponse[]
  created_at: string
  updated_at: string
}

export interface TripDetailsResponse {
  id: number
  name: string
  user_id: number
  start_location_text?: string | null
  start_latitude?: number | null
  start_longitude?: number | null
  num_days: number
  trip_mode: string
  budget_band: string
  companions?: string | null
  status: string
  days: TripDayResponse[]
  created_at: string
  updated_at: string
}

export interface ActiveTripSeedResponse {
  trip_seed_id: number
  conversation_id: number
  status: string
  num_days?: number | null
  trip_mode?: string | null
  budget_band?: string | null
  start_location_text?: string | null
  companions?: string | null
  is_complete: boolean
  missing_fields: string[]
  updated_at: string
}

export interface TripsListResponse {
  trips: TripResponse[]
  active_trip_seeds: ActiveTripSeedResponse[]
  total_trips: number
  total_active: number
}

export interface TripSeedStateResponse {
  trip_seed_id: number
  conversation_id: number
  num_days?: number | null
  trip_mode?: string | null
  budget_band?: string | null
  start_location_text?: string | null
  companions?: string | null
  status: string
  is_complete: boolean
  missing_fields: string[]
}

export interface TripSeedAgentResponse {
  response_text: string
  conversation_id: number
  trip_seed_state: TripSeedStateResponse
  is_complete: boolean
}

export interface MessageResponse {
  id: number
  role: string
  content: string
  created_at: string
}

export interface ConversationResponse {
  id: number
  user_id: number
  trip_id?: number | null
  agent_name?: string | null
  messages: MessageResponse[]
  created_at: string
  updated_at: string
}

export interface TripSeedMessageRequest {
  message: string
  conversation_id?: number | null
}

export interface CreateTripRequest {
  trip_seed_id: number
  name: string
}

export interface AttractionVibeInfo {
  vibe_id: number
  vibe_code: string
  vibe_label: string
  strength: number
}

export interface AttractionResponse {
  id: number
  name: string
  type: string
  description?: string | null
  city_id: number
  city_name: string
  latitude: number
  longitude: number
  url?: string | null
  price_level?: string | null
  hidden_gem_score?: number | null
  seasonality?: string | null
  vibes: AttractionVibeInfo[]
  created_at: string
  updated_at: string
}

export interface AttractionsListResponse {
  attractions: AttractionResponse[]
  total: number
  trip_id?: number | null
  matching_vibe_ids?: number[] | null
}

export interface CreateTripStopRequest {
  attraction_id?: number | null
  label?: string | null
  slot: string
  order_index: number
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

  /**
   * Trip-related endpoints
   */
  trips: {
    /**
     * Get all trips and active trip seeds for the current user
     */
    async getAll(): Promise<TripsListResponse> {
      return api.get<TripsListResponse>('/api/trips')
    },

    /**
     * Get trip details with days and stops
     */
    async getDetails(tripId: number): Promise<TripDetailsResponse> {
      return api.get<TripDetailsResponse>(`/api/trips/${tripId}`)
    },

    /**
     * Create a trip from a completed trip seed
     */
    async createFromSeed(request: CreateTripRequest): Promise<TripResponse> {
      return api.post<TripResponse>('/api/trips', request)
    },
  },

  /**
   * Trip seed conversation endpoints
   */
  tripSeed: {
    /**
     * Send a message to the trip seed agent
     */
    async sendMessage(request: TripSeedMessageRequest): Promise<TripSeedAgentResponse> {
      return api.post<TripSeedAgentResponse>('/api/trip-seed/message', request)
    },
  },

  /**
   * Conversation endpoints
   */
  conversations: {
    /**
     * Get conversation with messages by ID
     */
    async getById(conversationId: number): Promise<ConversationResponse> {
      return api.get<ConversationResponse>(`/api/trip-seed/conversations/${conversationId}`)
    },
  },

  /**
   * Attraction endpoints
   */
  attractions: {
    /**
     * Get attractions filtered by trip vibes
     */
    async getByTripId(tripId: number, limit?: number): Promise<AttractionsListResponse> {
      const params = new URLSearchParams()
      params.append('trip_id', tripId.toString())
      if (limit) {
        params.append('limit', limit.toString())
      }
      return api.get<AttractionsListResponse>(`/api/attractions?${params.toString()}`)
    },
  },

  /**
   * Trip stop endpoints
   */
  tripStops: {
    /**
     * Create a stop for a trip day
     */
    async create(
      tripId: number,
      dayId: number,
      request: CreateTripStopRequest
    ): Promise<TripStopResponse> {
      return api.post<TripStopResponse>(
        `/api/trips/${tripId}/days/${dayId}/stops`,
        request
      )
    },

    /**
     * Delete a stop
     */
    async delete(tripId: number, dayId: number, stopId: number): Promise<void> {
      return api.delete<void>(`/api/trips/${tripId}/days/${dayId}/stops/${stopId}`)
    },

    /**
     * Reorder stops within a day
     */
    async reorder(
      tripId: number,
      dayId: number,
      stopOrders: Array<{ stop_id: number; order_index: number }>
    ): Promise<TripStopResponse[]> {
      return api.patch<TripStopResponse[]>(
        `/api/trips/${tripId}/days/${dayId}/stops/reorder`,
        { stop_orders: stopOrders }
      )
    },
  },
}

export { ApiError }

