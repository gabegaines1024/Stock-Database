import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface User {
  id: number;
  email: string;
  username: string;
  created_at: string;
}

export interface UserCreate {
  email: string;
  username: string;
  password: string;
}

export interface Stock {
  id: number;
  ticker_symbol: string;
  company_name: string;
  sector?: string;
}

export interface StockBase {
  ticker_symbol: string;
  company_name: string;
  sector?: string;
}

export interface Portfolio {
  id: number;
  name: string;
  user_id: number;
  created_at: string;
}

export interface PortfolioBase {
  name: string;
  user_id: number;
}

export interface Transaction {
  id: number;
  portfolio_id: number;
  ticker_symbol: string;
  transaction_type: 'buy' | 'sell';
  quantity: number;
  price: number;
  executed_at: string;
}

export interface TransactionBase {
  portfolio_id: number;
  ticker_symbol: string;
  transaction_type: 'buy' | 'sell';
  quantity: number;
  price: number;
}

export interface StockPrice {
  ticker: string;
  price: number;
}

export interface StockSearchResult {
  query: string;
  results: Array<{
    '1. symbol': string;
    '2. name': string;
    '3. type': string;
    '4. region': string;
    '8. currency': string;
  }>;
}

// API Functions
export const apiService = {
  // Users
  users: {
    getAll: () => api.get<User[]>('/users'),
    getById: (id: number) => api.get<User>(`/users/${id}`),
    create: (data: UserCreate) => api.post<User>('/users', data),
  },

  // Stocks
  stocks: {
    getAll: () => api.get<Stock[]>('/stocks'),
    getById: (id: number) => api.get<Stock>(`/stocks/${id}`),
    create: (data: StockBase) => api.post<Stock>('/stocks', data),
    update: (id: number, data: Partial<StockBase>) => api.put<Stock>(`/stocks/${id}`, data),
    delete: (id: number) => api.delete<Stock>(`/stocks/${id}`),
    getPrice: (ticker: string) => api.get<StockPrice>(`/api/stocks/${ticker}/price`),
    search: (query: string) => api.get<StockSearchResult>('/api/stocks/search', { params: { query } }),
  },

  // Portfolios
  portfolios: {
    getAll: () => api.get<Portfolio[]>('/portfolios'),
    getById: (id: number) => api.get<Portfolio>(`/portfolios/${id}`),
    create: (data: PortfolioBase) => api.post<Portfolio>('/portfolios', data),
    update: (id: number, data: Partial<PortfolioBase>) => api.put<Portfolio>(`/portfolios/${id}`, data),
    delete: (id: number) => api.delete<Portfolio>(`/portfolios/${id}`),
  },

  // Transactions
  transactions: {
    getAll: () => api.get<Transaction[]>('/transactions'),
    getById: (id: number) => api.get<Transaction>(`/transactions/${id}`),
    create: (data: TransactionBase) => api.post<Transaction>('/transactions', data),
    update: (id: number, data: Partial<TransactionBase>) => api.put<Transaction>(`/transactions/${id}`, data),
    delete: (id: number) => api.delete<Transaction>(`/transactions/${id}`),
  },
};

export default api;

