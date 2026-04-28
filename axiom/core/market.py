import collections
import pandas as pd

class Market:
    """
    The central market for AXIOM. 
    Maintains a Limit Order Book (LOB) and handles order matching.
    """
    def __init__(self):
        self.bids = []  # Sorted high to low: (price, quantity, agent_id)
        self.asks = []  # Sorted low to high: (price, quantity, agent_id)
        self.trade_history = []
        self.last_price = 100.0  # Initial reference price

    def submit_order(self, order_type, price, quantity, agent_id):
        """
        Submit a limit order to the book.
        order_type: 'buy' or 'sell'
        """
        order = {"price": price, "quantity": quantity, "agent_id": agent_id}
        if order_type == 'buy':
            self.bids.append(order)
            self.bids.sort(key=lambda x: x['price'], reverse=True)
        elif order_type == 'sell':
            self.asks.append(order)
            self.asks.sort(key=lambda x: x['price'])
        
    def clear_double_auction(self):
        """
        Clears orders using a standard double auction matching mechanism.
        Matches the highest bids with the lowest asks.
        """
        executed_trades = []
        
        while self.bids and self.asks and self.bids[0]['price'] >= self.asks[0]['price']:
            bid = self.bids.pop(0)
            ask = self.asks.pop(0)
            
            # Transaction price is usually the mid-price or the price of the sitting order
            # Here we'll use the mid-price for the double auction
            match_price = (bid['price'] + ask['price']) / 2.0
            match_qty = min(bid['quantity'], ask['quantity'])
            
            trade = {
                "price": match_price,
                "quantity": match_qty,
                "buyer_id": bid['agent_id'],
                "seller_id": ask['agent_id']
            }
            executed_trades.append(trade)
            self.trade_history.append(trade)
            self.last_price = match_price
            
            # Handle partial fills
            if bid['quantity'] > match_qty:
                bid['quantity'] -= match_qty
                self.bids.insert(0, bid)
            if ask['quantity'] > match_qty:
                ask['quantity'] -= match_qty
                self.asks.insert(0, ask)
                
        return executed_trades

    def get_market_state(self):
        """
        Returns basic market metrics for observation.
        Includes order book depth.
        """
        best_bid = self.bids[0]['price'] if self.bids else self.last_price
        best_ask = self.asks[0]['price'] if self.asks else self.last_price
        
        # Depth: Cumulative volume at best 5 levels
        bid_depth = sum(b['quantity'] for b in self.bids[:5])
        ask_depth = sum(a['quantity'] for a in self.asks[:5])
        
        return {
            "last_price": self.last_price,
            "best_bid": best_bid,
            "best_ask": best_ask,
            "spread": (best_ask - best_bid),
            "bid_depth": bid_depth,
            "ask_depth": ask_depth,
            "volume": sum(t['quantity'] for t in self.trade_history[-10:])
        }

    def clear_walrasian(self):
        """
        Implements Walrasian price clearing (excess demand zeroing).
        Finds the price that minimizes |Demand - Supply|.
        """
        if not self.bids or not self.asks:
            return []

        # Define price range to search
        min_price = min(self.asks[0]['price'], self.bids[-1]['price'])
        max_price = max(self.bids[0]['price'], self.asks[-1]['price'])
        
        # Simple search across price points
        best_p = self.last_price
        min_excess = float('inf')
        
        # Scan 100 points between min and max price
        for p in [min_price + i*(max_price-min_price)/100 for i in range(101)]:
            demand = sum(b['quantity'] for b in self.bids if b['price'] >= p)
            supply = sum(a['quantity'] for a in self.asks if a['price'] <= p)
            excess = abs(demand - supply)
            if excess < min_excess:
                min_excess = excess
                best_p = p
        
        # Execute trades at best_p
        # For simplicity in this ABM, we match what we can at the equilibrium price
        match_qty = min(sum(b['quantity'] for b in self.bids if b['price'] >= best_p),
                        sum(a['quantity'] for a in self.asks if a['price'] <= best_p))
        
        # In a real Walrasian clearing, we would proportionally allocate match_qty
        # Here we'll just execute trades from the top of the books at best_p
        executed_trades = []
        remaining_qty = match_qty
        
        while remaining_qty > 0 and self.bids and self.asks:
            bid = self.bids[0]
            ask = self.asks[0]
            
            if bid['price'] < best_p or ask['price'] > best_p:
                break
                
            qty = min(bid['quantity'], ask['quantity'], remaining_qty)
            trade = {
                "price": best_p,
                "quantity": qty,
                "buyer_id": bid['agent_id'],
                "seller_id": ask['agent_id']
            }
            executed_trades.append(trade)
            self.trade_history.append(trade)
            
            bid['quantity'] -= qty
            ask['quantity'] -= qty
            remaining_qty -= qty
            
            if bid['quantity'] == 0: self.bids.pop(0)
            if ask['quantity'] == 0: self.asks.pop(0)
            
        self.last_price = best_p
        return executed_trades
