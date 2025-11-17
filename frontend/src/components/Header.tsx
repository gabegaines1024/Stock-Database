import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Header.css';

export const Header: React.FC = () => {
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <header className="header">
      <div className="header-container">
        <Link to="/" className="header-logo">
          <span className="logo-icon">📈</span>
          <span className="logo-text">StockTracker</span>
        </Link>
        
        <nav className="header-nav">
          <Link
            to="/"
            className={`nav-link ${isActive('/') ? 'active' : ''}`}
          >
            Dashboard
          </Link>
          <Link
            to="/stocks"
            className={`nav-link ${isActive('/stocks') ? 'active' : ''}`}
          >
            Stocks
          </Link>
          <Link
            to="/portfolios"
            className={`nav-link ${isActive('/portfolios') ? 'active' : ''}`}
          >
            Portfolios
          </Link>
          <Link
            to="/transactions"
            className={`nav-link ${isActive('/transactions') ? 'active' : ''}`}
          >
            Transactions
          </Link>
        </nav>
      </div>
    </header>
  );
};

