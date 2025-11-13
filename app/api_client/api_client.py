import os
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()


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
        try:
            data = self.fetch_stock_data(ticker)
            refreshed_at = data["Meta Data"]["3. Last Refreshed"]
            closing_price = data["Time Series (Daily)"][refreshed_at]["4. close"]
            return float(closing_price)
        except KeyError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Malformed response from stock data provider: missing field {exc}.",
            ) from exc
        except ValueError as exc:
            raise HTTPException(
                status_code=502,
                detail="Malformed response from stock data provider: non-numeric price value.",
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
        try:
            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=self.DEFAULT_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
        except requests.Timeout as exc:
            raise HTTPException(
                status_code=504,
                detail="Stock data provider timed out while processing the request.",
            ) from exc
        except requests.HTTPError as exc:
            status_code = exc.response.status_code if exc.response else 502
            message = exc.response.text if exc.response else str(exc)
            raise HTTPException(
                status_code=status_code,
                detail=f"API request failed: {message}",
            ) from exc
        except requests.RequestException as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Unable to reach stock data provider: {exc}",
            ) from exc

        try:
            payload: Dict[str, Any] = response.json()
        except ValueError as exc:
            raise HTTPException(
                status_code=502,
                detail="Stock data provider returned invalid JSON.",
            ) from exc

        if "Error Message" in payload:
            raise HTTPException(
                status_code=404,
                detail=payload["Error Message"],
            )

        if "Note" in payload:
            raise HTTPException(
                status_code=429,
                detail=payload["Note"],
            )

        return payload