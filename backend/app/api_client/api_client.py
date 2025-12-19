import os
from typing import Any, Dict, List
import logging

import requests
from dotenv import load_dotenv
from fastapi import HTTPException

from app.exceptions import ExternalServiceError

load_dotenv()

logger = logging.getLogger(__name__)


class StockAPIClient:
    """Client for interacting with the Alpha Vantage stock API."""

    DEFAULT_TIMEOUT_SECONDS = 10
    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self) -> None:
        self.api_key = os.getenv("API_KEY")
        if not self.api_key:
            raise RuntimeError("API_KEY environment variable is not set.")

    def fetch_stock_data(self, ticker: str) -> Dict[str, Any]:
        """Fetch time series stock data from Alpha Vantage."""
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": ticker,
            "apikey": self.api_key,
        }
        return self._perform_request(params)

    def get_current_price(self, ticker: str) -> float:
        """Get the latest closing price for a stock ticker."""
        logger.debug(f"Fetching current price for {ticker}")
        try:
            data = self.fetch_stock_data(ticker)
            refreshed_at = data["Meta Data"]["3. Last Refreshed"]
            closing_price = data["Time Series (Daily)"][refreshed_at]["4. close"]
            price = float(closing_price)
            logger.info(f"Successfully fetched price for {ticker}: ${price}")
            return price
        except KeyError as exc:
            logger.error(f"Malformed response from Alpha Vantage for {ticker}: missing field {exc}")
            raise ExternalServiceError(
                "Alpha Vantage",
                f"Malformed response: missing field {exc}",
                "MALFORMED_RESPONSE"
            ) from exc
        except ValueError as exc:
            logger.error(f"Invalid price value from Alpha Vantage for {ticker}: {exc}")
            raise ExternalServiceError(
                "Alpha Vantage",
                "Non-numeric price value in response",
                "INVALID_PRICE_VALUE"
            ) from exc

    def search_stocks(self, query: str) -> List[Dict[str, Any]]:
        """Search for stocks by keyword."""
        params = {
            "function": "SYMBOL_SEARCH",
            "keywords": query,
            "apikey": self.api_key,
        }
        data = self._perform_request(params)
        try:
            return data["bestMatches"]
        except KeyError as exc:
            raise HTTPException(
                status_code=502,
                detail="Malformed response from stock data provider: search results missing.",
            ) from exc

    def _perform_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a GET request against Alpha Vantage with robust error handling."""
        logger.debug(f"Making request to Alpha Vantage with params: {params.get('function')}")
        try:
            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=self.DEFAULT_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
        except requests.Timeout as exc:
            logger.warning(f"Alpha Vantage request timed out: {params.get('function')}")
            raise ExternalServiceError(
                "Alpha Vantage",
                "Request timed out",
                "TIMEOUT"
            ) from exc
        except requests.HTTPError as exc:
            status_code = exc.response.status_code if exc.response else 502
            message = exc.response.text if exc.response else str(exc)
            logger.error(f"Alpha Vantage HTTP error {status_code}: {message}")
            raise ExternalServiceError(
                "Alpha Vantage",
                f"HTTP {status_code}: {message}",
                "HTTP_ERROR"
            ) from exc
        except requests.RequestException as exc:
            logger.error(f"Alpha Vantage request failed: {str(exc)}")
            raise ExternalServiceError(
                "Alpha Vantage",
                f"Connection error: {str(exc)}",
                "CONNECTION_ERROR"
            ) from exc

        try:
            payload: Dict[str, Any] = response.json()
        except ValueError as exc:
            logger.error(f"Invalid JSON response from Alpha Vantage: {str(exc)}")
            raise ExternalServiceError(
                "Alpha Vantage",
                "Invalid JSON response",
                "INVALID_JSON"
            ) from exc

        if "Error Message" in payload:
            error_msg = payload["Error Message"]
            logger.warning(f"Alpha Vantage error message: {error_msg}")
            raise ExternalServiceError(
                "Alpha Vantage",
                error_msg,
                "API_ERROR"
            )

        if "Note" in payload:
            note = payload["Note"]
            logger.warning(f"Alpha Vantage rate limit note: {note}")
            raise ExternalServiceError(
                "Alpha Vantage",
                note,
                "RATE_LIMIT"
            )

        return payload