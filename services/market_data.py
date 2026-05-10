"""
行情数据获取服务
使用 yfinance 获取贵金属和期货数据
"""
import yfinance as yf
import pandas as pd
import streamlit as st
from config import DEFAULT_SYMBOLS, FUTURES_SYMBOLS, DATA_DAYS, KLINE_PERIODS


@st.cache_data(ttl=300, show_spinner="正在获取行情数据...")
def get_kline_data(symbol: str, period_key: str = "日K") -> pd.DataFrame:
    """
    获取K线数据

    Args:
        symbol: yfinance品种代码，如 GC=F
        period_key: K线周期，如 "日K"、"周K"、"月K"

    Returns:
        包含 OHLCV 数据的 DataFrame
    """
    interval = KLINE_PERIODS.get(period_key, "1d")
    days = DATA_DAYS.get(period_key, 365)

    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=f"{days}d", interval=interval)
        if df.empty:
            return pd.DataFrame()

        # 统一列名
        df = df.rename(columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        })

        # 确保索引为日期
        df.index = pd.to_datetime(df.index)
        df.index.name = "date"

        return df
    except Exception as e:
        st.warning(f"获取 {symbol} 数据失败: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=60, show_spinner="正在获取实时报价...")
def get_realtime_price(symbol: str) -> dict:
    """
    获取实时报价信息

    Args:
        symbol: yfinance品种代码

    Returns:
        包含价格、涨跌幅等信息的字典
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info

        current_price = info.get("lastPrice", None)
        previous_close = info.get("previousClose", None)

        if current_price and previous_close:
            change = current_price - previous_close
            change_pct = (change / previous_close) * 100
        else:
            # 回退到 history 获取
            hist = ticker.history(period="2d")
            if len(hist) >= 2:
                current_price = hist["Close"].iloc[-1]
                previous_close = hist["Close"].iloc[-2]
                change = current_price - previous_close
                change_pct = (change / previous_close) * 100
            elif len(hist) == 1:
                current_price = hist["Close"].iloc[0]
                change = 0
                change_pct = 0
            else:
                return {"price": 0, "change": 0, "change_pct": 0, "symbol": symbol}

        return {
            "symbol": symbol,
            "price": round(current_price, 2),
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
        }
    except Exception as e:
        return {
            "symbol": symbol,
            "price": 0,
            "change": 0,
            "change_pct": 0,
            "error": str(e),
        }


def get_all_default_prices() -> dict:
    """获取所有默认品种的实时报价"""
    results = {}
    for name, symbol in DEFAULT_SYMBOLS.items():
        results[name] = get_realtime_price(symbol)
    return results


def get_custom_futures_prices(custom_symbols: dict) -> dict:
    """获取自定义期货品种的实时报价"""
    results = {}
    for name, symbol in custom_symbols.items():
        results[name] = get_realtime_price(symbol)
    return results


def resolve_symbol(input_code: str) -> str:
    """
    解析品种代码，支持中文名称和yfinance代码
    """
    # 先在默认品种中查找
    for name, symbol in DEFAULT_SYMBOLS.items():
        if name == input_code or symbol == input_code:
            return symbol

    # 在期货品种中查找
    for name, symbol in FUTURES_SYMBOLS.items():
        if name == input_code or symbol == input_code:
            return symbol

    # 直接作为yfinance代码返回
    return input_code
