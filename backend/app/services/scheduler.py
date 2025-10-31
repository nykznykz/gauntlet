"""Background scheduler for periodic tasks"""
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.config import settings
from app.db.session import SessionLocal
from app.models.competition import Competition
from app.models.position import Position
from app.models.participant import Participant
from app.services.market_data_service import market_data_service
from app.services.cfd_engine import CFDEngine
from app.services.portfolio_manager import PortfolioManager
from app.services.llm_invoker import LLMInvoker

logger = logging.getLogger(__name__)


class SchedulerService:
    """Service for managing scheduled background tasks"""

    def __init__(self):
        self.scheduler = BackgroundScheduler(timezone=settings.TIMEZONE)
        self._is_running = False

    def start(self):
        """Start the scheduler with all configured jobs"""
        if not settings.SCHEDULER_ENABLED:
            logger.info("Scheduler is disabled in settings")
            return

        if self._is_running:
            logger.warning("Scheduler is already running")
            return

        # Add price update job
        self.scheduler.add_job(
            func=self._update_all_prices,
            trigger=IntervalTrigger(minutes=settings.PRICE_UPDATE_INTERVAL),
            id="update_prices",
            name="Update all position prices",
            replace_existing=True,
        )
        logger.info(f"Scheduled price updates every {settings.PRICE_UPDATE_INTERVAL} minute(s)")

        # Add LLM invocation job
        self.scheduler.add_job(
            func=self._invoke_all_participants,
            trigger=IntervalTrigger(minutes=settings.LLM_INVOCATION_INTERVAL),
            id="invoke_llms",
            name="Invoke LLMs for active participants",
            replace_existing=True,
        )
        logger.info(f"Scheduled LLM invocations every {settings.LLM_INVOCATION_INTERVAL} minute(s)")

        # Start the scheduler
        self.scheduler.start()
        self._is_running = True
        logger.info("Background scheduler started successfully")

    def shutdown(self):
        """Shutdown the scheduler gracefully"""
        if self._is_running:
            self.scheduler.shutdown(wait=True)
            self._is_running = False
            logger.info("Background scheduler shut down")

    def _update_all_prices(self):
        """Update prices for all open positions"""
        db = SessionLocal()
        try:
            logger.info("Starting price update task...")

            # Get all open positions
            positions = db.query(Position).all()

            if not positions:
                logger.info("No open positions to update")
                return

            # Group positions by symbol to batch price fetches
            symbols_needed = set(p.symbol for p in positions)
            logger.info(f"Fetching prices for {len(symbols_needed)} symbols: {symbols_needed}")

            # Fetch all prices at once
            prices = market_data_service.get_multiple_prices(list(symbols_needed), "crypto")

            if not prices:
                logger.warning("Failed to fetch any prices from Binance")
                return

            # Update each position
            cfd_engine = CFDEngine(db)
            portfolio_manager = PortfolioManager(db)
            updated_count = 0
            portfolios_to_update = set()

            for position in positions:
                current_price = prices.get(position.symbol)
                if current_price:
                    try:
                        cfd_engine.update_position_price(position, current_price)
                        portfolios_to_update.add(position.portfolio_id)
                        updated_count += 1
                    except Exception as e:
                        logger.error(f"Error updating position {position.id}: {e}")
                else:
                    logger.warning(f"No price available for {position.symbol}")

            # Update all affected portfolios and participant equity
            for portfolio_id in portfolios_to_update:
                try:
                    from app.models.portfolio import Portfolio
                    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
                    if portfolio:
                        portfolio = portfolio_manager.update_portfolio(portfolio)
                        # Update participant equity to reflect updated portfolio value
                        participant = db.query(Participant).filter(Participant.id == portfolio.participant_id).first()
                        if participant:
                            portfolio_manager.update_participant_equity(participant, portfolio.equity)
                except Exception as e:
                    logger.error(f"Error updating portfolio {portfolio_id}: {e}")

            logger.info(f"Price update complete: Updated {updated_count} positions across {len(portfolios_to_update)} portfolios")

        except Exception as e:
            logger.error(f"Error in price update task: {e}", exc_info=True)
        finally:
            db.close()

    def _invoke_all_participants(self):
        """Invoke LLMs for all active participants in active competitions"""
        db = SessionLocal()
        try:
            logger.info("Starting LLM invocation task...")

            # Get all active competitions (not ended yet)
            now = datetime.now()
            active_competitions = (
                db.query(Competition)
                .filter(Competition.end_time > now)
                .all()
            )

            if not active_competitions:
                logger.info("No active competitions found")
                return

            logger.info(f"Found {len(active_competitions)} active competition(s)")

            # Get all active participants in these competitions
            competition_ids = [c.id for c in active_competitions]
            active_participants = (
                db.query(Participant)
                .filter(
                    Participant.competition_id.in_(competition_ids),
                    Participant.status == "active"
                )
                .all()
            )

            if not active_participants:
                logger.info("No active participants to invoke")
                return

            logger.info(f"Invoking {len(active_participants)} participant(s)...")

            # Invoke each participant
            llm_invoker = LLMInvoker(db)
            success_count = 0
            error_count = 0

            for participant in active_participants:
                try:
                    logger.info(f"Invoking participant {participant.name} ({participant.id})...")
                    invocation = llm_invoker.invoke_participant(participant.id)

                    if invocation and invocation.status == "success":
                        success_count += 1
                        logger.info(f"✓ Successfully invoked {participant.name}")
                    else:
                        error_count += 1
                        logger.warning(f"✗ Failed to invoke {participant.name}: {invocation.status if invocation else 'No invocation'}")

                except Exception as e:
                    error_count += 1
                    logger.error(f"Error invoking participant {participant.id}: {e}")

            logger.info(f"LLM invocation complete: {success_count} successful, {error_count} failed")

        except Exception as e:
            logger.error(f"Error in LLM invocation task: {e}", exc_info=True)
        finally:
            db.close()


# Global scheduler instance
scheduler_service = SchedulerService()
