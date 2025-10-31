const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ApiResponse<T> {
  data: T;
  error?: string;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return { data };
    } catch (error) {
      return {
        data: null as T,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  async get<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  async post<T>(endpoint: string, body: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  async put<T>(endpoint: string, body: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(body),
    });
  }

  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }
}

export const apiClient = new ApiClient(API_BASE_URL);

// Competition APIs
export const competitionApi = {
  list: () => apiClient.get('/api/v1/competitions'),
  get: (id: string) => apiClient.get(`/api/v1/competitions/${id}`),
  create: (data: any) => apiClient.post('/api/v1/competitions', data),
  history: (id: string) => apiClient.get(`/api/v1/competitions/${id}/history`),
};

// Participant APIs
export const participantApi = {
  list: (competitionId: string) =>
    apiClient.get(`/api/v1/participants/competitions/${competitionId}/all`),
  get: (id: string) => apiClient.get(`/api/v1/participants/${id}`),
  performance: (id: string) => apiClient.get(`/api/v1/participants/${id}/performance`),
};

// Portfolio APIs
export const portfolioApi = {
  get: (participantId: string) =>
    apiClient.get(`/api/v1/participants/${participantId}/portfolio`),
  history: (participantId: string, limit?: number) =>
    apiClient.get(`/api/v1/participants/${participantId}/history?limit=${limit || 500}`),
};

// Position APIs
export const positionApi = {
  list: (participantId: string) =>
    apiClient.get(`/api/v1/participants/${participantId}/positions`),
};

// Trade APIs
export const tradeApi = {
  list: (participantId: string, limit?: number) =>
    apiClient.get(`/api/v1/participants/${participantId}/trades?limit=${limit || 50}`),
};

// Market Data APIs
export const marketDataApi = {
  latest: (symbol: string) => apiClient.get(`/api/market-data/${symbol}/latest`),
  history: (symbol: string, params?: { start?: string; end?: string; interval?: string }) =>
    apiClient.get(`/api/market-data/${symbol}/history?${new URLSearchParams(params as any)}`),
};

// Leaderboard API
export const leaderboardApi = {
  get: (competitionId: string) =>
    apiClient.get(`/api/v1/leaderboard/competitions/${competitionId}/leaderboard`),
};

// Invocation APIs
export const invocationApi = {
  list: (participantId: string, options?: { limit?: number; offset?: number; status?: string }) => {
    const params = new URLSearchParams();
    if (options?.limit) params.append('limit', options.limit.toString());
    if (options?.offset) params.append('offset', options.offset.toString());
    if (options?.status) params.append('status', options.status);
    const query = params.toString();
    return apiClient.get(`/api/v1/participants/${participantId}/invocations${query ? '?' + query : ''}`);
  },
};
