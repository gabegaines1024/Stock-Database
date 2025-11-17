import React, { useState, useEffect } from 'react';
import { apiService, Stock, StockSearchResult } from '../services/api';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import './StockSearch.css';

export const StockSearch: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<StockSearchResult['results']>([]);
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedStock, setSelectedStock] = useState<Stock | null>(null);
  const [price, setPrice] = useState<number | null>(null);
  const [priceLoading, setPriceLoading] = useState(false);

  useEffect(() => {
    loadStocks();
  }, []);

  const loadStocks = async () => {
    try {
      const response = await apiService.stocks.getAll();
      setStocks(response.data);
    } catch (error) {
      console.error('Error loading stocks:', error);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    setLoading(true);
    try {
      const response = await apiService.stocks.search(searchQuery);
      setSearchResults(response.data.results || []);
    } catch (error) {
      console.error('Error searching stocks:', error);
      setSearchResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleGetPrice = async (ticker: string) => {
    setPriceLoading(true);
    setSelectedStock(null);
    try {
      const response = await apiService.stocks.getPrice(ticker);
      setPrice(response.data.price);
      setSelectedStock({ id: 0, ticker_symbol: ticker, company_name: '' });
    } catch (error) {
      console.error('Error getting price:', error);
      setPrice(null);
    } finally {
      setPriceLoading(false);
    }
  };

  const handleAddStock = async (symbol: string, name: string) => {
    try {
      await apiService.stocks.create({
        ticker_symbol: symbol,
        company_name: name,
      });
      await loadStocks();
      alert('Stock added successfully!');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Error adding stock');
    }
  };

  return (
    <div className="stock-search">
      <div className="container">
        <div className="page-header slide-up">
          <h1>Stock Search</h1>
          <p>Search for stocks and get real-time prices</p>
        </div>

        <Card className="search-card fade-in">
          <div className="search-container">
            <input
              type="text"
              className="search-input"
              placeholder="Search for stocks (e.g., AAPL, Microsoft)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
            <Button onClick={handleSearch} disabled={loading}>
              {loading ? 'Searching...' : 'Search'}
            </Button>
          </div>
        </Card>

        {price !== null && selectedStock && (
          <Card className="price-card fade-in">
            <div className="price-display">
              <h2>{selectedStock.ticker_symbol}</h2>
              <div className="price-value">${price.toFixed(2)}</div>
            </div>
          </Card>
        )}

        {searchResults.length > 0 && (
          <Card className="results-card fade-in">
            <h2 className="card-title">Search Results</h2>
            <div className="results-list">
              {searchResults.map((result, index) => (
                <div key={index} className="result-item">
                  <div className="result-info">
                    <div className="result-symbol">{result['1. symbol']}</div>
                    <div className="result-name">{result['2. name']}</div>
                    <div className="result-type">{result['3. type']} • {result['4. region']}</div>
                  </div>
                  <div className="result-actions">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleGetPrice(result['1. symbol'])}
                      disabled={priceLoading}
                    >
                      Get Price
                    </Button>
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={() => handleAddStock(result['1. symbol'], result['2. name'])}
                    >
                      Add to List
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}

        <Card className="stocks-list-card fade-in">
          <h2 className="card-title">Your Tracked Stocks</h2>
          {stocks.length === 0 ? (
            <p className="empty-state">No stocks tracked yet. Search and add stocks to get started!</p>
          ) : (
            <div className="stocks-grid">
              {stocks.map((stock) => (
                <div key={stock.id} className="stock-item">
                  <div className="stock-info">
                    <div className="stock-symbol">{stock.ticker_symbol}</div>
                    <div className="stock-name">{stock.company_name}</div>
                    {stock.sector && <div className="stock-sector">{stock.sector}</div>}
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleGetPrice(stock.ticker_symbol)}
                    disabled={priceLoading}
                  >
                    Get Price
                  </Button>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};

