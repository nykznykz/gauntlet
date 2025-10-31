# API Keys Setup Guide

Complete guide to obtaining all required API keys for the Gauntlet platform.

## Required API Keys

1. **Anthropic API Key** (Required) - For Claude LLM trading agents
2. **OpenAI API Key** (Optional) - For GPT trading agents
3. **Binance API Key** (NOT NEEDED!) - Uses free public endpoints automatically

---

## 1. Anthropic API Key (Claude)

### Step-by-Step Instructions

#### Option A: Sign Up for Anthropic Console

1. **Visit Anthropic Console**
   - Go to: https://console.anthropic.com/

2. **Create Account**
   - Click "Sign Up" or "Get Started"
   - Use your email address
   - Verify your email

3. **Add Payment Method**
   - Click on "Billing" in the left sidebar
   - Add a credit card or payment method
   - Anthropic charges pay-as-you-go (no subscription)
   - **Pricing**: ~$3 per million input tokens, ~$15 per million output tokens for Claude 3.5 Sonnet

4. **Generate API Key**
   - Click "API Keys" in the left sidebar
   - Click "Create Key"
   - Give it a name (e.g., "Gauntlet Trading Platform")
   - Copy the API key (starts with `sk-ant-`)
   - **IMPORTANT**: Save it immediately - you won't see it again!

5. **Set Usage Limits (Recommended)**
   - In Billing section, set a monthly spending limit
   - Start with $10-20 for testing
   - This prevents unexpected charges

6. **Add to Your .env File**
   ```env
   ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

### Anthropic Pricing (as of 2024)

**Claude 3.5 Sonnet** (Recommended for trading):
- Input: $3 / million tokens (~$0.003 per 1K tokens)
- Output: $15 / million tokens (~$0.015 per 1K tokens)

**Estimated Costs**:
- Per LLM invocation: ~$0.05 - $0.15 (depending on prompt size)
- 100 invocations: ~$5 - $15
- Daily trading (96 invocations/day at 15-min intervals): ~$5 - $15/day

**Claude 3.5 Haiku** (Cheaper, faster):
- Input: $1 / million tokens
- Output: $5 / million tokens
- ~60% cheaper but less sophisticated reasoning

### Testing Your Key

```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 100,
    "messages": [{"role": "user", "content": "Say hello"}]
  }'
```

### Troubleshooting

- **"Invalid API Key"**: Make sure you copied the entire key including `sk-ant-`
- **"Insufficient credits"**: Add a payment method in the Billing section
- **Rate limits**: Free tier has lower limits; add payment for higher limits

---

## 2. OpenAI API Key (GPT)

### Step-by-Step Instructions

1. **Visit OpenAI Platform**
   - Go to: https://platform.openai.com/

2. **Create Account**
   - Click "Sign up"
   - Use email, Google, Microsoft, or Apple account
   - Verify your email

3. **Add Payment Method**
   - Click your profile icon → "Billing"
   - Click "Add payment method"
   - Add credit card
   - **Note**: OpenAI requires prepaid credits
   - Add $5-20 to start

4. **Generate API Key**
   - Click your profile icon → "API keys"
   - Or visit: https://platform.openai.com/api-keys
   - Click "Create new secret key"
   - Give it a name (e.g., "Gauntlet Trading")
   - Copy the key (starts with `sk-`)
   - **IMPORTANT**: Save immediately - you won't see it again!

5. **Set Usage Limits (Recommended)**
   - Go to "Billing" → "Usage limits"
   - Set a monthly hard limit (e.g., $20)
   - Set email notifications

6. **Add to Your .env File**
   ```env
   OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

### OpenAI Pricing (as of 2024)

**GPT-4 Turbo** (Recommended for trading):
- Input: $10 / million tokens (~$0.01 per 1K tokens)
- Output: $30 / million tokens (~$0.03 per 1K tokens)

**GPT-4o** (Latest, balanced):
- Input: $5 / million tokens
- Output: $15 / million tokens

**GPT-3.5 Turbo** (Budget option):
- Input: $0.50 / million tokens
- Output: $1.50 / million tokens
- Much cheaper but less sophisticated

**Estimated Costs**:
- Per invocation (GPT-4): ~$0.10 - $0.30
- Per invocation (GPT-3.5): ~$0.01 - $0.03
- Daily trading with GPT-4: ~$10 - $30/day
- Daily trading with GPT-3.5: ~$1 - $3/day

### Testing Your Key

```bash
curl https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4-turbo-preview",
    "messages": [{"role": "user", "content": "Say hello"}],
    "max_tokens": 50
  }'
```

### Troubleshooting

- **"Invalid API Key"**: Check you copied the full key starting with `sk-`
- **"Insufficient quota"**: Add more credits in Billing section
- **"Model not found"**: You need GPT-4 access (automatic with paid account)
- **Rate limits**: New accounts have lower limits; increase over time

---

## 3. Binance API Key (NOT REQUIRED!)

### ✅ No API Key Needed!

**The platform now uses Binance public endpoints by default** - no signup or API key required!

- **✅ FREE**: Public API is completely free
- **✅ No Account**: No Binance account needed
- **✅ Real-time Prices**: Live crypto prices for BTC, ETH, SOL, BNB, etc.
- **✅ Good Rate Limits**: 1200 requests/minute (more than enough)
- **✅ Works Out of Box**: Just start the backend and it works!

### When Would You Need an API Key?

You only need a Binance API key if:
- You need **higher rate limits** (unlikely for this use case)
- You want to access **private account data** (we don't)

**For Gauntlet, you can skip this entirely!**

### Step-by-Step Instructions

1. **Create Binance Account**
   - Go to: https://www.binance.com/
   - Click "Register"
   - Use email or phone number
   - Complete verification (KYC may be required depending on region)

2. **Enable Two-Factor Authentication (Required)**
   - Go to Profile → Security
   - Enable Google Authenticator or SMS 2FA
   - **REQUIRED** before creating API keys

3. **Create API Key**
   - Go to Profile → API Management
   - Click "Create API"
   - Choose "System generated" (not third-party)
   - Label it (e.g., "Gauntlet Market Data")
   - Complete 2FA verification
   - Save both:
     - API Key
     - Secret Key

4. **Configure API Restrictions (IMPORTANT)**
   - After creating, click "Edit restrictions"
   - **Enable ONLY**: "Enable Reading" ✅
   - **Disable**: "Enable Spot & Margin Trading" ❌
   - **Disable**: "Enable Futures" ❌
   - **Disable**: "Enable Withdrawals" ❌
   - This makes the key read-only for safety!

5. **IP Access (Optional)**
   - Can restrict to specific IP addresses
   - Or leave as "Unrestricted" for development

6. **Add to Your .env File**
   ```env
   BINANCE_API_KEY=your_binance_api_key
   BINANCE_API_SECRET=your_binance_secret_key
   ```

### Binance Pricing

- **Free**: Market data API is completely free
- **Rate Limits**:
  - 1200 requests per minute (weight-based)
  - More than enough for our use case

### Alternative: Use Without API Key

You can also use Binance's public endpoints without an API key:

```python
# In app/market/binance.py, you can use:
exchange = ccxt.binance({
    'enableRateLimit': True,
    # No apiKey or secret needed for public data
})
```

Rate limits are lower but sufficient for testing.

### Testing Your Key

```python
import ccxt

exchange = ccxt.binance({
    'apiKey': 'your_api_key',
    'secret': 'your_secret_key',
})

# Test fetching Bitcoin price
ticker = exchange.fetch_ticker('BTC/USDT')
print(f"Bitcoin price: ${ticker['last']}")
```

### Troubleshooting

- **"Invalid API Key"**: Check you copied both API key and secret correctly
- **"IP restricted"**: Add your current IP or set to unrestricted
- **"Permission denied"**: Make sure "Enable Reading" is turned on

---

## Quick Setup Checklist

### Minimum Required (Start Here)

- [ ] **Anthropic API Key** - Required for Claude trading agents
  - Visit: https://console.anthropic.com/
  - Add $10-20 credits to start
  - Cost: ~$5-15 per day of active trading

### Already Working (No Setup Needed!)

- ✅ **Binance Market Data** - Uses public API automatically
  - No signup required
  - No API key needed
  - Free real-time crypto prices
  - Works out of the box!

### Optional (Add Later)

- [ ] **OpenAI API Key** - For GPT trading agents (alternative to Claude)
  - Visit: https://platform.openai.com/
  - Add $10-20 credits
  - Cost: ~$10-30/day (GPT-4) or ~$1-3/day (GPT-3.5)

---

## Updating Your .env File

Once you have your keys, update `backend/.env`:

```env
# Database (already configured)
DATABASE_URL=postgresql://gauntlet_user:secure_password@localhost:5432/gauntlet
REDIS_URL=redis://localhost:6379/0

# LLM API Keys (ADD YOUR KEYS HERE)
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxx    # ← Paste your Anthropic key
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx      # ← Paste your OpenAI key (optional)

# Market Data (ADD YOUR KEYS HERE - Optional)
BINANCE_API_KEY=your_binance_api_key            # ← Paste your Binance key
BINANCE_API_SECRET=your_binance_secret_key      # ← Paste your Binance secret

# Application (already configured)
SECRET_KEY=dev-secret-key-change-in-production
API_KEY=dev-api-key
LOG_LEVEL=INFO
ENVIRONMENT=development

# Scheduler
SCHEDULER_ENABLED=false
TIMEZONE=UTC

# Redis Cache TTL
PRICE_CACHE_TTL=60
LEADERBOARD_CACHE_TTL=300

# Server
HOST=0.0.0.0
PORT=8000
```

---

## Cost Estimates

### Development/Testing (Light Usage)

**Anthropic Claude 3.5 Sonnet**:
- Testing (10-20 invocations): $1-3
- Weekly budget: $10-20

**OpenAI GPT-4**:
- Testing (10-20 invocations): $2-5
- Weekly budget: $15-30

**OpenAI GPT-3.5**:
- Testing (10-20 invocations): $0.20-0.50
- Weekly budget: $2-5

**Binance**: FREE

### Production (Active Competition)

Assuming 15-minute intervals (96 invocations/day):

**Claude 3.5 Sonnet**:
- Per day: $5-15
- Per week: $35-105
- Per month: $150-450

**GPT-4 Turbo**:
- Per day: $10-30
- Per week: $70-210
- Per month: $300-900

**GPT-3.5 Turbo** (Budget option):
- Per day: $1-3
- Per week: $7-21
- Per month: $30-90

### Cost Optimization Tips

1. **Start with less frequent invocations**
   - Test with 1-hour intervals instead of 15 minutes
   - Reduces costs by 75%

2. **Use cheaper models for testing**
   - Claude Haiku: 60% cheaper than Sonnet
   - GPT-3.5: 90% cheaper than GPT-4

3. **Set spending limits**
   - Both Anthropic and OpenAI allow hard limits
   - Set low limits while testing

4. **Use mock mode**
   - Test with mock LLM responses first
   - No API calls = zero cost

---

## Testing Without API Keys (Mock Mode)

You can test the entire platform without any API keys using mock data:

### Backend Mock Mode

Create `backend/app/llm/mock_client.py`:

```python
"""Mock LLM client for testing without API keys"""
from app.llm.base import BaseLLMClient
import json

class MockLLMClient(BaseLLMClient):
    """Mock client that returns predefined responses"""

    def invoke(self, prompt: str, config: dict = None) -> tuple[str, int, int]:
        # Mock response - always buys 0.1 BTC with 2x leverage
        response = {
            "decision": "trade",
            "reasoning": "Mock response: Buying BTC based on simulated analysis",
            "orders": [
                {
                    "action": "open",
                    "symbol": "BTCUSDT",
                    "side": "buy",
                    "quantity": 0.1,
                    "leverage": 2.0
                }
            ]
        }

        response_text = json.dumps(response)
        return response_text, 1000, 500  # Mock token counts
```

Then use it in testing without real API keys!

---

## Security Best Practices

### ✅ DO:
- Store API keys in `.env` file (not in code)
- Add `.env` to `.gitignore`
- Use read-only Binance keys
- Set spending limits on LLM APIs
- Rotate keys periodically
- Use different keys for dev/prod

### ❌ DON'T:
- Commit API keys to Git
- Share keys publicly
- Give Binance keys trading permissions
- Use production keys in development
- Store keys in frontend code

---

## Next Steps

1. **Start with Anthropic only**
   - Get Claude API key first
   - Test with a few invocations
   - Costs ~$1-3 for initial testing

2. **Test with Mock Mode**
   - Verify everything works without API costs
   - Build confidence in the platform

3. **Add Real Keys**
   - Start with low spending limits
   - Monitor costs in dashboards
   - Scale up as needed

4. **Optimize Costs**
   - Use cheaper models for testing
   - Reduce invocation frequency
   - Implement caching

---

## Support & Resources

### Anthropic
- Dashboard: https://console.anthropic.com/
- Documentation: https://docs.anthropic.com/
- Pricing: https://www.anthropic.com/pricing
- Support: support@anthropic.com

### OpenAI
- Dashboard: https://platform.openai.com/
- Documentation: https://platform.openai.com/docs
- Pricing: https://openai.com/pricing
- Support: https://help.openai.com/

### Binance
- Dashboard: https://www.binance.com/en/my/settings/api-management
- API Docs: https://binance-docs.github.io/apidocs/
- Support: https://www.binance.com/en/support

---

## Summary

**To get started quickly:**

1. Sign up for Anthropic: https://console.anthropic.com/
2. Add $10-20 credits
3. Generate API key
4. Paste into `backend/.env`
5. Start testing!

**✅ Binance works automatically** - Uses free public API, no signup needed!

**OpenAI is optional** - Only needed if you want GPT agents competing alongside Claude.

**Total minimum investment to start: $10-20 (just Anthropic credits)**

That's it! Just one API key and you're ready to run LLM trading competitions! 🚀
