#!/usr/bin/env python3
"""
Test Binance public API without any API keys
Run this to verify market data works before setting up anything else
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.market.binance import BinanceProvider

def test_binance_public_api():
    """Test that Binance public API works without keys"""
    print("=" * 60)
    print("Testing Binance Public API (No Keys Required)")
    print("=" * 60)
    print()

    try:
        # Initialize provider (will use public endpoints)
        provider = BinanceProvider()
        print("✅ Binance provider initialized\n")

        # Test symbols
        test_symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT"]

        print("Fetching current prices...")
        print("-" * 60)

        success_count = 0
        for symbol in test_symbols:
            try:
                price = provider.get_current_price(symbol)
                if price:
                    print(f"✅ {symbol:12} ${price:>12,.2f}")
                    success_count += 1
                else:
                    print(f"❌ {symbol:12} Failed to fetch price")
            except Exception as e:
                print(f"❌ {symbol:12} Error: {str(e)}")

        print("-" * 60)
        print(f"\nResults: {success_count}/{len(test_symbols)} successful")

        if success_count == len(test_symbols):
            print("\n🎉 Success! Binance public API is working perfectly!")
            print("✅ No API key needed - ready to use for trading competitions")
            return True
        else:
            print("\n⚠️  Some symbols failed - but public API is accessible")
            print("This is usually temporary. Try again in a moment.")
            return False

    except Exception as e:
        print(f"\n❌ Error testing Binance API: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check your internet connection")
        print("2. Binance may be temporarily down (rare)")
        print("3. Try again in a few minutes")
        return False


if __name__ == "__main__":
    print()
    success = test_binance_public_api()
    print()

    if success:
        print("Next steps:")
        print("1. Get your Anthropic API key from https://console.anthropic.com/")
        print("2. Add it to backend/.env")
        print("3. Start the backend and create your first competition!")
        sys.exit(0)
    else:
        print("Please check the errors above and try again.")
        sys.exit(1)
