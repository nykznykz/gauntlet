"""LLM Invoker service"""
import json
import time
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from sqlalchemy.orm import Session
from uuid import UUID
from app.models.participant import Participant
from app.models.competition import Competition
from app.models.portfolio import Portfolio
from app.models.position import Position
from app.models.order import Order
from app.models.llm_invocation import LLMInvocation
from app.llm.anthropic_client import AnthropicClient
from app.llm.openai_client import OpenAIClient
from app.llm.azure_openai_client import AzureOpenAIClient
from app.llm.deepseek_client import DeepSeekClient
from app.llm.qwen_client import QwenClient
from app.llm.prompt_builder import prompt_builder
from app.services.market_data_service import market_data_service
from app.services.trading_engine import TradingEngine
from app.schemas.llm_response import LLMResponse, LLMOrderDecision


class LLMInvoker:
    """Service for invoking LLM and processing trading decisions"""

    def __init__(self, db: Session):
        self.db = db
        self.trading_engine = TradingEngine(db)

    def _get_llm_client(self, provider: str):
        """Get appropriate LLM client"""
        if provider == "anthropic":
            return AnthropicClient()
        elif provider == "openai":
            return OpenAIClient()
        elif provider == "azure_openai":
            return AzureOpenAIClient()
        elif provider == "deepseek":
            return DeepSeekClient()
        elif provider == "qwen":
            return QwenClient()
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    def invoke_participant(
        self,
        participant_id: UUID
    ) -> Optional[LLMInvocation]:
        """Invoke LLM for a participant and process the trading decision"""

        # Load participant and related data
        participant = self.db.query(Participant).filter(Participant.id == participant_id).first()
        if not participant or participant.status != "active":
            return None

        competition = self.db.query(Competition).filter(Competition.id == participant.competition_id).first()
        portfolio = self.db.query(Portfolio).filter(Portfolio.participant_id == participant_id).first()
        positions = self.db.query(Position).filter(Position.participant_id == participant_id).all()

        # Get market data
        available_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"]
        market_data = self._fetch_market_data(available_symbols)

        # Get leaderboard
        leaderboard = self._get_leaderboard(competition.id)

        # Build prompt
        prompt_text = prompt_builder.build_trading_prompt(
            competition=competition,
            participant=participant,
            portfolio=portfolio,
            positions=positions,
            market_data=market_data,
            leaderboard=leaderboard,
        )

        # Create invocation record
        invocation = LLMInvocation(
            participant_id=participant.id,
            competition_id=competition.id,
            prompt_text=prompt_text,
            status="pending",
        )
        self.db.add(invocation)
        self.db.commit()
        self.db.refresh(invocation)

        # Invoke LLM
        start_time = time.time()

        try:
            llm_client = self._get_llm_client(participant.llm_provider)
            response_text, prompt_tokens, response_tokens = llm_client.invoke(
                prompt_text,
                config=participant.llm_config or {}
            )

            response_time_ms = int((time.time() - start_time) * 1000)

            # Update invocation with response
            invocation.response_text = response_text
            invocation.prompt_tokens = prompt_tokens
            invocation.response_tokens = response_tokens
            invocation.response_time_ms = response_time_ms

            # Parse and validate response
            try:
                parsed_decision = self._parse_llm_response(response_text)
                invocation.parsed_decision = parsed_decision.model_dump()
                invocation.status = "success"

                # Process trading decisions
                if parsed_decision.decision == "trade" and parsed_decision.orders:
                    self._process_orders(
                        participant=participant,
                        competition=competition,
                        portfolio=portfolio,
                        orders=parsed_decision.orders,
                        invocation_id=invocation.id
                    )

            except Exception as e:
                invocation.status = "invalid_response"
                invocation.error_message = f"Failed to parse response: {str(e)}"

        except Exception as e:
            response_time_ms = int((time.time() - start_time) * 1000)
            invocation.status = "error"
            invocation.error_message = str(e)
            invocation.response_time_ms = response_time_ms

        self.db.add(invocation)
        self.db.commit()
        self.db.refresh(invocation)

        return invocation

    def _parse_llm_response(self, response_text: str) -> LLMResponse:
        """Parse and validate LLM response JSON"""
        # Extract JSON from response (may have markdown code blocks)
        response_text = response_text.strip()

        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1])

        # Parse JSON
        data = json.loads(response_text)

        # Validate with Pydantic
        return LLMResponse(**data)

    def _process_orders(
        self,
        participant: Participant,
        competition: Competition,
        portfolio: Portfolio,
        orders: List[LLMOrderDecision],
        invocation_id: UUID
    ):
        """Process orders from LLM decision"""

        for order_decision in orders:
            # Validate order
            position_id = UUID(order_decision.position_id) if order_decision.position_id else None

            is_valid, rejection_reason = self.trading_engine.validate_order(
                participant=participant,
                competition=competition,
                portfolio=portfolio,
                symbol=order_decision.symbol,
                side=order_decision.side,
                quantity=Decimal(str(order_decision.quantity)),
                leverage=Decimal(str(order_decision.leverage)),
                action=order_decision.action,
                position_id=position_id,
            )

            # Create order record
            order = Order(
                participant_id=participant.id,
                competition_id=competition.id,
                symbol=order_decision.symbol,
                asset_class="crypto",  # TODO: determine from symbol
                order_type="market",
                side=order_decision.side,
                quantity=Decimal(str(order_decision.quantity)),
                leverage=Decimal(str(order_decision.leverage)),
                status="pending" if is_valid else "rejected",
                rejection_reason=rejection_reason,
                llm_invocation_id=invocation_id,
            )

            self.db.add(order)
            self.db.commit()
            self.db.refresh(order)

            # Execute if valid
            if is_valid:
                self.trading_engine.execute_order(order, order_decision.action)

    def _fetch_market_data(self, symbols: List[str]) -> dict:
        """Fetch market data for symbols"""
        prices = market_data_service.get_multiple_prices(symbols, "crypto")

        market_data = {
            "available_symbols": symbols,
            "prices": [
                {
                    "symbol": symbol,
                    "asset_class": "crypto",
                    "current_price": float(price) if price else None,
                }
                for symbol, price in prices.items()
            ]
        }

        return market_data

    def _get_leaderboard(self, competition_id: UUID) -> List[dict]:
        """Get current leaderboard for competition"""
        participants = (
            self.db.query(Participant)
            .filter(Participant.competition_id == competition_id)
            .order_by(Participant.current_equity.desc())
            .all()
        )

        leaderboard = []
        for rank, p in enumerate(participants, 1):
            total_pnl_pct = float((p.current_equity - p.initial_capital) / p.initial_capital * 100)
            leaderboard.append({
                "rank": rank,
                "name": p.name,
                "equity": float(p.current_equity),
                "pnl_pct": total_pnl_pct,
            })

        return leaderboard
