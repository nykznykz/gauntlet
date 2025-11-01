export interface Competition {
  id: string;
  name: string;
  status: "upcoming" | "active" | "completed";
  start_time: string;
  end_time: string;
  initial_capital: number;
  max_leverage: number;
  invocation_interval_minutes: number;
}

export interface Participant {
  id: string;
  competition_id: string;
  name: string;
  llm_provider: string;
  llm_model: string;
  llm_config: Record<string, any> | null;
  status: "active" | "liquidated" | "disqualified";
  joined_at: string;
  current_equity: number;
  initial_capital: number;
  peak_equity: number;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  endpoint_url: string | null;
  timeout_seconds: number;
  created_at: string;
  updated_at: string;
}

export interface Portfolio {
  id: string;
  participant_id: string;
  updated_at: string;
  equity: number;
  cash_balance: number;
  unrealized_pnl: number;
  realized_pnl: number;
  margin_used: number;
  margin_available: number;
  total_pnl: number;
  current_leverage: number;
  margin_level: number | null;
}

export interface Position {
  id: string;
  portfolio_id: string;
  symbol: string;
  side: "long" | "short";
  quantity: number;
  entry_price: number;
  current_price: number;
  unrealized_pnl: number;
  margin_used: number;
  leverage: number;
  opened_at: string;
}

export interface Trade {
  id: string;
  participant_id: string;
  symbol: string;
  side: "long" | "short";
  action: "open" | "close";
  quantity: number;
  price: number;
  pnl: number | null;
  timestamp: string;
  llm_reasoning: string | null;
}

export interface MarketData {
  symbol: string;
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface TickerPrice {
  symbol: string;
  price: number;
  change_24h: number;
  change_percent_24h: number;
}

export interface PortfolioHistoryPoint {
  recorded_at: string;
  equity: number;
  cash_balance: number;
  margin_used: number;
  realized_pnl: number;
  unrealized_pnl: number;
  total_pnl: number;
}

export interface PortfolioHistory {
  participant_id: string;
  participant_name: string;
  history: PortfolioHistoryPoint[];
}

export interface MultiParticipantHistory {
  participants: PortfolioHistory[];
}

export interface LeaderboardEntry {
  rank: number;
  participant_id: string;
  name: string;
  equity: number;
  total_pnl: number;
  total_pnl_pct: number;
  total_trades: number;
  win_rate: number;
  status: string;
}

export interface ExecutionResult {
  order_id: string;
  action: string;
  symbol: string;
  side: string | null;
  quantity: number | null;
  leverage: number;
  validation_passed: boolean;
  rejection_reason: string | null;
  status: string;
  executed_price: number | null;
}

export interface LLMInvocation {
  id: string;
  participant_id: string;
  competition_id: string;

  // Request
  prompt_text: string;
  prompt_tokens: number | null;
  market_data_snapshot: Record<string, any> | null;
  portfolio_snapshot: Record<string, any> | null;

  // Response
  response_text: string | null;
  response_tokens: number | null;
  parsed_decision: Record<string, any> | null;
  execution_results: ExecutionResult[] | null;

  // Metadata
  invocation_time: string;
  response_time_ms: number | null;
  status: "success" | "timeout" | "error" | "invalid_response";
  error_message: string | null;

  // Cost Tracking
  estimated_cost: number | null;
}

export interface LLMInvocationList {
  invocations: LLMInvocation[];
  total: number;
  limit: number;
  offset: number;
}
