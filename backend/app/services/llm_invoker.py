"""LLM Invoker service"""
import json
import logging
import re
import time
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from sqlalchemy.orm import Session
from uuid import UUID

logger = logging.getLogger(__name__)
from app.models.participant import Participant
from app.models.competition import Competition
from app.models.portfolio import Portfolio
from app.models.position import Position
from app.models.order import Order
from app.models.llm_invocation import LLMInvocation
from app.llm.aws_bedrock_client import AWSBedrockClient
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
            # Use AWS Bedrock for Claude models
            return AWSBedrockClient()
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

        # Build prompt (now returns system and user prompts)
        system_prompt, user_prompt = prompt_builder.build_trading_prompt(
            competition=competition,
            participant=participant,
            portfolio=portfolio,
            positions=positions,
            market_data=market_data,
            leaderboard=leaderboard,
        )

        # Create invocation record (store user prompt for compatibility)
        invocation = LLMInvocation(
            participant_id=participant.id,
            competition_id=competition.id,
            prompt_text=user_prompt,  # Store user prompt for now
            status="pending",
        )
        self.db.add(invocation)
        self.db.commit()
        self.db.refresh(invocation)

        # Invoke LLM with both prompts
        start_time = time.time()

        try:
            llm_client = self._get_llm_client(participant.llm_provider)
            response_text, prompt_tokens, response_tokens = llm_client.invoke(
                prompt=user_prompt,
                config=participant.llm_config or {},
                system_prompt=system_prompt
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
                    execution_results = self._process_orders(
                        participant=participant,
                        competition=competition,
                        portfolio=portfolio,
                        orders=parsed_decision.orders,
                        invocation_id=invocation.id
                    )
                    invocation.execution_results = execution_results

            except Exception as e:
                # Ensure response_text is preserved even when parsing fails
                if not invocation.response_text:
                    invocation.response_text = response_text
                invocation.status = "invalid_response"
                invocation.error_message = f"Failed to parse response: {str(e)}"
                logger.warning(f"Failed to parse LLM response for participant {participant.id}: {str(e)}. Response length: {len(response_text) if response_text else 0}")

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
        """Parse and validate LLM response JSON with robust extraction"""
        response_text = response_text.strip()

        # Strategy 0: Extract from [Response] section (for DeepSeek Reasoner format)
        if "[Response]" in response_text:
            response_section_match = re.search(r'\[Response\]\s*(.*?)(?:\n\[|$)', response_text, re.DOTALL)
            if response_section_match:
                response_section = response_section_match.group(1).strip()
                # Try to extract JSON from this section
                first_brace = response_section.find('{')
                last_brace = response_section.rfind('}')
                if first_brace != -1 and last_brace != -1:
                    try:
                        json_str = response_section[first_brace:last_brace + 1]
                        data = json.loads(json_str)
                        return LLMResponse(**data)
                    except (json.JSONDecodeError, ValueError):
                        pass

        # Strategy 1: Extract JSON from markdown code blocks (```json or ```)
        if "```" in response_text:
            # Find all code blocks - more flexible pattern to handle various formats
            # Match ```json or ``` followed by content and closing ```
            # Allow optional whitespace/newlines around content
            code_block_pattern = r'```(?:json)?\s*(.*?)```'
            matches = re.findall(code_block_pattern, response_text, re.DOTALL)

            if matches:
                # Try each code block until we find valid JSON
                for block in matches:
                    try:
                        data = json.loads(block.strip())
                        return LLMResponse(**data)
                    except (json.JSONDecodeError, ValueError):
                        continue

        # Strategy 2: Try to find JSON object boundaries { ... }
        # Look for the first { and last } to extract JSON
        first_brace = response_text.find('{')
        last_brace = response_text.rfind('}')

        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            try:
                json_str = response_text[first_brace:last_brace + 1]
                data = json.loads(json_str)
                return LLMResponse(**data)
            except (json.JSONDecodeError, ValueError):
                pass

        # Strategy 3: Try parsing the whole response as-is (in case it's clean JSON)
        try:
            data = json.loads(response_text)
            return LLMResponse(**data)
        except (json.JSONDecodeError, ValueError):
            pass

        # If all strategies fail, raise an error with helpful message
        raise ValueError(
            f"Could not extract valid JSON from response. "
            f"Response preview: {response_text[:200]}..."
        )

    def _process_orders(
        self,
        participant: Participant,
        competition: Competition,
        portfolio: Portfolio,
        orders: List[LLMOrderDecision],
        invocation_id: UUID
    ) -> List[dict]:
        """Process orders from LLM decision and return execution results"""

        execution_results = []

        for order_decision in orders:
            # For close actions, get side, quantity, and symbol from the existing position if not provided
            side = order_decision.side
            quantity = order_decision.quantity
            position_id = UUID(order_decision.position_id) if order_decision.position_id else None

            # Determine symbol - for close actions, ALWAYS use the position's actual symbol
            # to prevent LLM confusion from causing wrong price fetching
            symbol = order_decision.symbol  # Default: use LLM's symbol
            position = None

            if order_decision.action == "close" and position_id:
                # Get the position to extract side, quantity, and SYMBOL
                position = self.db.query(Position).filter(Position.id == position_id).first()
                if position:
                    # CRITICAL FIX: Use position's actual symbol, not LLM's claim
                    symbol = position.symbol
                    if side is None:
                        # For closing, the side is opposite of the position side
                        side = "sell" if position.side == "long" else "buy"
                    if quantity is None:
                        quantity = float(position.quantity)

            # Validate that we have required fields
            if side is None or quantity is None:
                rejection_reason = "Missing required fields: side and/or quantity"
                order = Order(
                    participant_id=participant.id,
                    competition_id=competition.id,
                    symbol=symbol,  # Use corrected symbol
                    asset_class="crypto",
                    order_type="market",
                    side=side or "buy",
                    quantity=Decimal(str(quantity or 0)),
                    leverage=Decimal(str(order_decision.leverage)),
                    status="rejected",
                    rejection_reason=rejection_reason,
                    llm_invocation_id=invocation_id,
                )
                self.db.add(order)
                self.db.commit()
                self.db.refresh(order)

                execution_results.append({
                    "order_id": str(order.id),
                    "action": order_decision.action,
                    "symbol": symbol,  # Use corrected symbol
                    "side": side,
                    "quantity": float(quantity) if quantity else None,
                    "leverage": float(order_decision.leverage),
                    "validation_passed": False,
                    "rejection_reason": rejection_reason,
                    "status": "rejected"
                })
                continue

            is_valid, rejection_reason = self.trading_engine.validate_order(
                participant=participant,
                competition=competition,
                portfolio=portfolio,
                symbol=symbol,  # Use corrected symbol
                side=side,
                quantity=Decimal(str(quantity)),
                leverage=Decimal(str(order_decision.leverage)),
                action=order_decision.action,
                position_id=position_id,
            )

            # Create order record
            order = Order(
                participant_id=participant.id,
                competition_id=competition.id,
                symbol=symbol,  # Use corrected symbol
                asset_class="crypto",  # TODO: determine from symbol
                order_type="market",
                side=side,
                quantity=Decimal(str(quantity)),
                leverage=Decimal(str(order_decision.leverage)),
                status="pending" if is_valid else "rejected",
                rejection_reason=rejection_reason,
                llm_invocation_id=invocation_id,
            )

            self.db.add(order)
            self.db.commit()
            self.db.refresh(order)

            # Execute if valid
            execution_status = "rejected"
            if is_valid:
                # Extract exit_plan if provided
                exit_plan_dict = None
                if order_decision.exit_plan:
                    exit_plan_dict = order_decision.exit_plan.model_dump(exclude_none=True)

                self.trading_engine.execute_order(order, order_decision.action, position_id, exit_plan_dict)
                # Refresh to get updated status
                self.db.refresh(order)
                execution_status = order.status

            execution_results.append({
                "order_id": str(order.id),
                "action": order_decision.action,
                "symbol": symbol,  # Use corrected symbol
                "side": side,
                "quantity": float(quantity),
                "leverage": float(order_decision.leverage),
                "validation_passed": is_valid,
                "rejection_reason": rejection_reason,
                "status": execution_status,
                "executed_price": float(order.executed_price) if order.executed_price else None
            })

        return execution_results

    def _fetch_market_data(self, symbols: List[str]) -> dict:
        """Fetch enhanced market data with price history and technical indicators"""
        # Fetch enhanced market data (similar to nof1.ai approach)
        # Includes: historical prices, volume, technical indicators (EMA, MACD, RSI)
        enhanced_data = market_data_service.get_enhanced_market_data(
            symbols=symbols,
            asset_class="crypto",
            timeframe="3m",  # 3-minute intervals like nof1.ai
            limit=20  # Last 20 candles (1 hour of 3-min data) - reduced to stay within token limits
        )

        market_data = {
            "available_symbols": symbols,
            "markets": enhanced_data  # Each market has: symbol, current_price, price_history, technical_indicators
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
