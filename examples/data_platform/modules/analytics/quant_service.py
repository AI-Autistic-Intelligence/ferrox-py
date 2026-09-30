import pandas as pd
import numpy as np
import random
from typing import Dict, Any, List
from structlog import get_logger

logger = get_logger()

class QuantitativeAnalyticsService:
    """
    Computes statistical anomalies and order book imbalances.
    In a real scenario, this extracts the last N minutes of data from Postgres.
    For this demo, we simulate the historical distribution based on current data.
    """
    
    def compute_order_book_imbalance(self, bids: List[List[float]], asks: List[List[float]]) -> Dict[str, Any]:
        """
        OBI = (BidVolume - AskVolume) / (BidVolume + AskVolume)
        Values near +1 indicate heavy buy-side spoofing/pressure.
        Values near -1 indicate heavy sell-side spoofing/pressure.
        """
        if not bids or not asks:
            return {"obi": 0.0, "status": "Neutral", "spoofing_detected": False}
            
        bid_vol = sum(price * qty for price, qty in bids)
        ask_vol = sum(price * qty for price, qty in asks)
        
        total = bid_vol + ask_vol
        if total == 0:
            return {"obi": 0.0, "status": "Neutral", "spoofing_detected": False}
            
        obi = (bid_vol - ask_vol) / total
        
        status = "Neutral"
        spoofing = False
        if obi > 0.7:
            status = "Extreme Buy Pressure"
            spoofing = obi > 0.9
        elif obi < -0.7:
            status = "Extreme Sell Pressure"
            spoofing = obi < -0.9
            
        return {
            "obi": round(obi, 4),
            "status": status,
            "spoofing_detected": spoofing,
            "bid_volume": round(bid_vol, 2),
            "ask_volume": round(ask_vol, 2)
        }
        
    def detect_whale_anomalies(self, current_price: float, current_volume: float) -> Dict[str, Any]:
        """
        Computes Z-Score against a simulated historical rolling window.
        Z = (x - mean) / std_dev
        If Z > 3, it's a massive anomaly (Whale).
        """
        # Simulate last 100 trades volume distribution (Log-normal distribution typical for crypto volumes)
        simulated_history = np.random.lognormal(mean=np.log(current_volume*0.2), sigma=0.8, size=100)
        df = pd.DataFrame(simulated_history, columns=['volume'])
        
        mean_vol = df['volume'].mean()
        std_vol = df['volume'].std()
        
        # Inject the current volume to see how it compares
        z_score = (current_volume - mean_vol) / (std_vol if std_vol > 0 else 1)
        
        is_whale = z_score > 3.0
        
        return {
            "z_score": round(z_score, 2),
            "mean_volume": round(mean_vol, 2),
            "is_whale_anomaly": bool(is_whale),
            "severity": "CRITICAL" if z_score > 5 else ("HIGH" if is_whale else "NORMAL")
        }
        
    def compute_cross_asset_correlation(self, asset1_prices: List[float], asset2_prices: List[float]) -> float:
        """
        Pearson correlation coefficient between two assets.
        """
        if len(asset1_prices) != len(asset2_prices) or len(asset1_prices) < 2:
            return 0.0
            
        df = pd.DataFrame({'a1': asset1_prices, 'a2': asset2_prices})
        corr = df['a1'].corr(df['a2'])
        
        return round(corr, 4) if not pd.isna(corr) else 0.0
