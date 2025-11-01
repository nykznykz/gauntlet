# Frontend Execution Results Display

## Overview
The frontend now displays complete execution results for each LLM invocation, making it easy to see why trades are or aren't being placed.

## Visual Layout

### 1. Summary Row (Collapsed View)
Each invocation shows at-a-glance execution status:

```
┌─────────────────────────────────────────────────────────────────────────┐
│ ✓ SUCCESS  11/01 10:30:42  250ms  Tokens: 1593/250  [✓ 2] [✗ 1]  ▼     │
└─────────────────────────────────────────────────────────────────────────┘
```

**New Badges**:
- `[✓ 2]` - Green badge showing 2 orders successfully executed
- `[✗ 1]` - Red badge showing 1 order rejected

### 2. Expanded View with Execution Results

```
┌─────────────────────────────────────────────────────────────────────────┐
│ ✓ SUCCESS  11/01 10:30:42  250ms  Tokens: 1593/250  [✓ 0] [✗ 1]  ▲     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│ Prompt Sent to LLM:                                                      │
│ ┌───────────────────────────────────────────────────────────────────┐  │
│ │ {                                                                  │  │
│ │   "competition_context": { ... },                                 │  │
│ │   "portfolio": { "cash_balance": 10000, ... }                     │  │
│ │ }                                                                  │  │
│ └───────────────────────────────────────────────────────────────────┘  │
│                                                                           │
│ LLM Response:                                                            │
│ ┌───────────────────────────────────────────────────────────────────┐  │
│ │ ```json                                                            │  │
│ │ {                                                                  │  │
│ │   "decision": "trade",                                             │  │
│ │   "reasoning": "BTC momentum strong",                              │  │
│ │   "orders": [...]                                                  │  │
│ │ }                                                                  │  │
│ │ ```                                                                │  │
│ └───────────────────────────────────────────────────────────────────┘  │
│                                                                           │
│ Parsed Trading Decision:                                                 │
│ ┌───────────────────────────────────────────────────────────────────┐  │
│ │ {                                                                  │  │
│ │   "decision": "trade",                                             │  │
│ │   "reasoning": "BTC momentum strong",                              │  │
│ │   "orders": [                                                      │  │
│ │     {                                                              │  │
│ │       "action": "open",                                            │  │
│ │       "symbol": "BTCUSDT",                                         │  │
│ │       "side": "buy",                                               │  │
│ │       "quantity": 0.0459,                                          │  │
│ │       "leverage": 2.0                                              │  │
│ │     }                                                              │  │
│ │   ]                                                                │  │
│ │ }                                                                  │  │
│ └───────────────────────────────────────────────────────────────────┘  │
│                                                                           │
│ Order Execution Results:                                                 │
│                                                                           │
│ ┌─────────────────────────────────────────────────────────────────┐    │
│ │ ✗  Order #1: OPEN BTCUSDT                                        │    │
│ │                                                                   │    │
│ │    Side: buy | Quantity: 0.04590000 | Leverage: 2x              │    │
│ │    Status: REJECTED                                              │    │
│ │                                                                   │    │
│ │    ┌───────────────────────────────────────────────────────┐    │    │
│ │    │ Rejected: Position size 5015.68578 exceeds max        │    │    │
│ │    │           5000.0000                                    │    │    │
│ │    └───────────────────────────────────────────────────────┘    │    │
│ └─────────────────────────────────────────────────────────────────┘    │
│                                                                           │
│ ┌─────────────────────────────────────────────────────────────────┐    │
│ │ ✓  Order #2: OPEN ETHUSDT                                        │    │
│ │                                                                   │    │
│ │    Side: buy | Quantity: 0.78500000 | Leverage: 1.5x            │    │
│ │    Status: EXECUTED | Executed @ $3,847.25                       │    │
│ └─────────────────────────────────────────────────────────────────┘    │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

## Color Coding

### Success (Green)
- **Background**: Light green (`bg-green-50` / `dark:bg-green-900/20`)
- **Border**: Green (`border-green-200` / `dark:border-green-800`)
- **Icon**: Green checkmark (✓)
- **Text**: Green (`text-green-700` / `dark:text-green-400`)

### Rejection (Red)
- **Background**: Light red (`bg-red-50` / `dark:bg-red-900/20`)
- **Border**: Red (`border-red-200` / `dark:border-red-800`)
- **Icon**: Red X (✗)
- **Text**: Red (`text-red-700` / `dark:text-red-400`)

## Data Flow

```
Backend Flow:
┌─────────────┐
│ LLM Invoked │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Response Parsed │
└──────┬──────────┘
       │
       ▼
┌──────────────────┐     ┌──────────────────────────┐
│ Orders Validated │ ──> │ execution_results[]      │
└──────────────────┘     │  - order_id              │
                         │  - validation_passed     │
                         │  - rejection_reason      │
                         │  - status                │
                         │  - executed_price        │
                         └──────────────────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │ Saved to DB:             │
                         │ llm_invocations table    │
                         │ execution_results column │
                         └──────────────────────────┘

Frontend Flow:
┌─────────────────┐
│ API Call        │
│ GET /invocations│
└──────┬──────────┘
       │
       ▼
┌─────────────────────────┐
│ LLMInvocationResponse   │
│ includes:               │
│  - prompt_text          │
│  - response_text        │
│  - parsed_decision      │
│  - execution_results ◄── NEW!
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│ InvocationLogs.tsx      │
│ displays:               │
│  - Summary badges       │
│  - Execution details    │
│  - Rejection reasons    │
└─────────────────────────┘
```

## Key Benefits

1. **Instant Debugging**: See why orders fail without checking backend logs
2. **At-a-Glance Status**: Summary badges show success/failure counts
3. **Complete Audit Trail**: Full flow from prompt to execution visible in one place
4. **Clear Rejection Reasons**: Prominent display of why orders were rejected
5. **Dark Mode Support**: All styling works in both light and dark themes

## Example Use Cases

### Use Case 1: GPT-4o Mini Position Sizing Issue
**Before**: "Why does GPT-4o mini have 0 positions?"
**After**: Expand invocation → See red badge → See rejection: "Position size 5015.68578 exceeds max 5000.0000"
**Result**: Immediately understand the model is calculating quantities incorrectly

### Use Case 2: Successful Trade
**Before**: Check positions table, check trades table, correlate timestamps
**After**: See green badge in summary → Expand → See "✓ Order #1: OPEN BTCUSDT | Status: EXECUTED | Executed @ $109,234"
**Result**: Instant confirmation of successful trade execution

### Use Case 3: Partial Success
**Before**: Unclear if any orders succeeded
**After**: See badges `[✓ 2] [✗ 1]` → Know 2 succeeded, 1 failed before even expanding
**Result**: Quick assessment of invocation effectiveness

## Technical Details

### Backend Schema Addition
```python
class LLMInvocationResponse(BaseModel):
    # ... existing fields ...
    execution_results: Optional[List[Dict[str, Any]]] = None
```

### Frontend Type Addition
```typescript
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
  // ... existing fields ...
  execution_results: ExecutionResult[] | null;
}
```

### Component Structure
```tsx
{invocation.execution_results && invocation.execution_results.length > 0 && (
  <div>
    <h4>Order Execution Results:</h4>
    <div className="space-y-2">
      {invocation.execution_results.map((result, idx) => (
        <div className={result.validation_passed ? 'green' : 'red'}>
          {result.validation_passed ? <CheckCircle /> : <XCircle />}
          <div>Order #{idx + 1}: {result.action} {result.symbol}</div>
          {result.rejection_reason && (
            <div className="rejection-box">
              <strong>Rejected:</strong> {result.rejection_reason}
            </div>
          )}
        </div>
      ))}
    </div>
  </div>
)}
```
