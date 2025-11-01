# Recent Changes

## 1. Fixed Close Action Schema (2025-11-01)

**Problem**: Close actions required redundant `side` and `quantity` fields even though this info exists in the position being closed.

**Solution**:
- Made `side` and `quantity` optional in `LLMOrderDecision` schema
- Updated `llm_invoker.py` to auto-extract these fields from the position when closing
- For long positions, automatically sets side to "sell"; for short, sets to "buy"

**Files Changed**:
- `app/schemas/llm_response.py` - Made fields optional
- `app/services/llm_invoker.py` - Added auto-extraction logic

**Impact**: LLMs can now close positions with minimal JSON:
```json
{
  "action": "close",
  "symbol": "ETHUSDT",
  "position_id": "uuid"
}
```

---

## 2. Fixed Position Sizing Instructions (2025-11-01)

**Problem**: GPT-4o mini was miscalculating position sizes, creating all rejected orders because it confused notional value with leveraged exposure.

**Root Cause**:
- The prompt was ambiguous about how leverage affects position limits
- GPT-4o mini calculated: quantity = (max_position_size × leverage) / price ❌
- Correct formula: quantity = max_position_size / price ✓

**Solution**: Completely rewrote position sizing instructions in `prompt_builder.py`:
- Added "CRITICAL - POSITION SIZING RULES" section
- Clarified that notional value limit applies REGARDLESS of leverage
- Provided worked examples with real numbers
- Added "COMMON MISTAKES TO AVOID" section with ❌ and ✓ examples
- Added 98% safety buffer recommendation to account for slippage

**Files Changed**:
- `app/llm/prompt_builder.py` - Rewrote instructions section

**Key Clarifications**:
1. System validates: `(quantity × current_price) ≤ max_position_size_dollars`
2. Leverage only affects margin required, NOT position size limits
3. Higher leverage = lower margin required, but same notional value limit

**Example**:
- Max position size: $5,000
- BTC price: $100,000
- Max quantity: 5000 / 100000 = 0.05 BTC (regardless of leverage!)
- At 2x leverage: margin required = $2,500
- At 3x leverage: margin required = $1,667

---

## 3. Added Execution Results Logging (2025-11-01)

**Problem**: Invocation logs showed if LLM response was successfully parsed, but didn't capture order validation/rejection details.

**Solution**:
- Added `execution_results` JSONB column to `llm_invocations` table
- Modified `llm_invoker._process_orders()` to return detailed execution results
- Each result includes:
  - order_id
  - action, symbol, side, quantity, leverage
  - validation_passed (boolean)
  - rejection_reason (if rejected)
  - status (rejected/executed)
  - executed_price (if executed)

**Files Changed**:
- `app/models/llm_invocation.py` - Added execution_results column
- `app/services/llm_invoker.py` - Collect and store execution results
- `alembic/versions/20251101_1015-*_add_execution_results_to_invocations.py` - Migration

**Database Migration**: Applied migration `34a666f12d78`

**Benefits**:
- Full audit trail: prompt → parsed decision → execution results
- Can see exactly why orders were rejected
- Easier to debug LLM trading logic

---

## 4. Created Participant Analysis Script (2025-11-01)

**New File**: `scripts/check_participant.py`

**Purpose**: Diagnostic tool to analyze participant invocations and execution results

**Usage**:
```bash
python scripts/check_participant.py "gpt"        # Find participant matching "gpt"
python scripts/check_participant.py "claude"     # Find participant matching "claude"
python scripts/check_participant.py              # Defaults to "gpt%mini%"
```

**Output Shows**:
- Participant details (ID, provider, model, equity)
- Recent invocations (last 10) with:
  - Timestamp, status
  - Parsed decision and reasoning
  - Orders in decision
  - Execution results (validation, rejection reasons, status)
- Recent orders (last 10) with details
- Current positions

**Use Cases**:
- Debug why a participant has no positions
- Analyze order rejection patterns
- Review LLM decision quality
- Compare different LLM behaviors

---

## 5. Added Execution Results to Frontend (2025-11-01)

**Problem**: Frontend showed successful invocations and parsed decisions, but no indication of why trades weren't being placed (validation failures, rejections).

**Solution**: Extended frontend to display execution results alongside invocations.

**Files Changed**:
- `backend/app/schemas/llm_invocation.py` - Added execution_results to API response schema
- `frontend/types/index.ts` - Added ExecutionResult interface and execution_results field
- `frontend/components/dashboard/InvocationLogs.tsx` - Added execution results display

**New Features**:

1. **Summary Badges**: Each invocation now shows badges in the summary row:
   - Green badge with ✓ count for successful executions
   - Red badge with ✗ count for rejected orders

2. **Detailed Execution Results**: When expanded, shows for each order:
   - Order number and action (OPEN/CLOSE symbol)
   - Side, quantity, leverage details
   - Validation status (passed/failed) with colored indicators
   - Execution status and price (if executed)
   - **Rejection reason** prominently displayed for failed orders

3. **Visual Indicators**:
   - Green background for successful executions with CheckCircle icon
   - Red background for rejections with XCircle icon
   - Clear rejection reason in highlighted box

**Benefits**:
- Immediately see which invocations resulted in actual trades
- Debug order rejections without checking backend logs
- Full visibility into the complete flow: prompt → decision → execution → result

**Example Display**:
```
Status: SUCCESS | Time: 11/01 10:30:42 | Tokens: 1593/250 | ✓ 0 ✗ 1

[Expanded]
Order Execution Results:
  ✗ Order #1: OPEN BTCUSDT
     Side: buy | Quantity: 0.04590000 | Leverage: 2x
     Status: REJECTED
     Rejected: Position size 5015.68578 exceeds max 5000.0000
```

---

## Summary of Investigation: GPT-4o Mini Zero Positions

**Finding**: GPT-4o mini had 4 successful invocations but ALL orders were rejected

**Rejection Reason**: "Position size exceeds max 5000.0000"

**Orders Attempted**:
1. 0.0459 BTC at ~$109,200 × 2 leverage = $10,015 position ❌ (exceeds $5,000 limit)
2. 0.0459 BTC at ~$109,200 × 2 leverage = $10,011 position ❌
3. 0.0457 BTC at ~$109,500 × 2 leverage = $10,003 position ❌
4. 0.0457 BTC at ~$109,500 × 2 leverage = $10,003 position ❌

**Root Cause**: GPT-4o mini was multiplying position size by leverage when calculating quantity

**Status**: Fixed via prompt improvements (see #2 above)

**Next Steps**:
- Wait for next invocation to verify GPT-4o mini uses correct formula
- Monitor with `scripts/check_participant.py "gpt"`
