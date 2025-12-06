type PriceUpdateCallback = (ticker: string, price: number) => void;
type ErrorCallback = (error: string) => void;

class StockPriceWebSocket {
  private ws: WebSocket | null = null;
  private priceCallbacks: Map<string, Set<PriceUpdateCallback>> = new Map();
  private errorCallbacks: Set<ErrorCallback> = new Set();
  private subscribedTickers: Set<string> = new Set();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 3000;
  private isConnecting = false;

  constructor() {
    // Auto-reconnect on close
    this.connect();
  }

  private getWebSocketUrl(): string {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    // Convert http:// to ws:// and https:// to wss://
    const wsUrl = apiUrl.replace(/^http/, 'ws');
    return `${wsUrl}/ws/prices`;
  }

  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) {
      return;
    }

    this.isConnecting = true;
    const url = this.getWebSocketUrl();
    
    try {
      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        
        // Resubscribe to all previously subscribed tickers
        this.subscribedTickers.forEach(ticker => {
          this.subscribe(ticker);
        });
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'price_update') {
            const { ticker, price } = data;
            this.notifyPriceUpdate(ticker, price);
          } else if (data.type === 'error') {
            this.notifyError(data.message || 'Unknown error');
          } else if (data.type === 'pong') {
            // Heartbeat response
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.isConnecting = false;
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.isConnecting = false;
        this.ws = null;
        
        // Attempt to reconnect
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          setTimeout(() => {
            this.connect();
          }, this.reconnectDelay);
        } else {
          this.notifyError('Failed to connect to price service. Please refresh the page.');
        }
      };
    } catch (error) {
      console.error('Error creating WebSocket:', error);
      this.isConnecting = false;
    }
  }

  subscribe(ticker: string, callback?: PriceUpdateCallback): void {
    const upperTicker = ticker.toUpperCase();
    
    if (callback) {
      if (!this.priceCallbacks.has(upperTicker)) {
        this.priceCallbacks.set(upperTicker, new Set());
      }
      this.priceCallbacks.get(upperTicker)!.add(callback);
    }

    if (!this.subscribedTickers.has(upperTicker)) {
      this.subscribedTickers.add(upperTicker);
      
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({
          type: 'subscribe',
          ticker: upperTicker,
        }));
      }
    }
  }

  unsubscribe(ticker: string, callback?: PriceUpdateCallback): void {
    const upperTicker = ticker.toUpperCase();
    
    if (callback) {
      const callbacks = this.priceCallbacks.get(upperTicker);
      if (callbacks) {
        callbacks.delete(callback);
        if (callbacks.size === 0) {
          this.priceCallbacks.delete(upperTicker);
        }
      }
    }

    // Only unsubscribe from WebSocket if no callbacks remain
    if (!this.priceCallbacks.has(upperTicker) || this.priceCallbacks.get(upperTicker)!.size === 0) {
      this.subscribedTickers.delete(upperTicker);
      
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({
          type: 'unsubscribe',
          ticker: upperTicker,
        }));
      }
    }
  }

  onError(callback: ErrorCallback): void {
    this.errorCallbacks.add(callback);
  }

  offError(callback: ErrorCallback): void {
    this.errorCallbacks.delete(callback);
  }

  private notifyPriceUpdate(ticker: string, price: number): void {
    const upperTicker = ticker.toUpperCase();
    const callbacks = this.priceCallbacks.get(upperTicker);
    if (callbacks) {
      callbacks.forEach(callback => {
        try {
          callback(upperTicker, price);
        } catch (error) {
          console.error('Error in price update callback:', error);
        }
      });
    }
  }

  private notifyError(error: string): void {
    this.errorCallbacks.forEach(callback => {
      try {
        callback(error);
      } catch (err) {
        console.error('Error in error callback:', err);
      }
    });
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.priceCallbacks.clear();
    this.subscribedTickers.clear();
    this.errorCallbacks.clear();
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

// Export singleton instance
export const stockPriceWebSocket = new StockPriceWebSocket();

