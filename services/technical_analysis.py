"""
技术指标计算服务
使用 pandas-ta 计算各类技术指标
"""
import pandas as pd
import pandas_ta as ta
from config import MACD_FAST, MACD_SLOW, MACD_SIGNAL, KDJ_PERIOD, RSI_PERIOD, MA_PERIODS


def calc_ma(df: pd.DataFrame, periods: list = None) -> pd.DataFrame:
    """
    计算移动均线

    Args:
        df: 包含 close 列的 DataFrame
        periods: 均线周期列表

    Returns:
        添加了 MA 列的 DataFrame
    """
    if periods is None:
        periods = MA_PERIODS

    df = df.copy()
    for p in periods:
        df[f"MA{p}"] = ta.sma(df["close"], length=p)
    return df


def calc_macd(
    df: pd.DataFrame,
    fast: int = MACD_FAST,
    slow: int = MACD_SLOW,
    signal: int = MACD_SIGNAL,
) -> pd.DataFrame:
    """
    计算 MACD 指标

    Args:
        df: 包含 close 列的 DataFrame
        fast: 快线周期
        slow: 慢线周期
        signal: 信号线周期

    Returns:
        添加了 MACD 列的 DataFrame
    """
    df = df.copy()
    macd = ta.macd(df["close"], fast=fast, slow=slow, signal=signal)
    if macd is not None and not macd.empty:
        col_names = macd.columns.tolist()
        df["MACD_DIF"] = macd.iloc[:, 0]
        df["MACD_SIGNAL"] = macd.iloc[:, 1]
        df["MACD_HIST"] = macd.iloc[:, 2]
    return df


def calc_kdj(
    df: pd.DataFrame,
    period: int = KDJ_PERIOD,
) -> pd.DataFrame:
    """
    计算 KDJ 指标

    Args:
        df: 包含 high, low, close 列的 DataFrame
        period: KDJ 周期

    Returns:
        添加了 KDJ 列的 DataFrame
    """
    df = df.copy()
    stoch = ta.stoch(
        df["high"], df["low"], df["close"],
        k=period, d=3, smooth_k=3,
    )
    if stoch is not None and not stoch.empty:
        df["K"] = stoch.iloc[:, 0]
        df["D"] = stoch.iloc[:, 1]
        # J = 3K - 2D
        df["J"] = 3 * df["K"] - 2 * df["D"]
    return df


def calc_rsi(df: pd.DataFrame, period: int = RSI_PERIOD) -> pd.DataFrame:
    """
    计算 RSI 指标

    Args:
        df: 包含 close 列的 DataFrame
        period: RSI 周期

    Returns:
        添加了 RSI 列的 DataFrame
    """
    df = df.copy()
    df["RSI"] = ta.rsi(df["close"], length=period)
    return df


def calc_volume_ma(df: pd.DataFrame, periods: list = None) -> pd.DataFrame:
    """
    计算成交量均线

    Args:
        df: 包含 volume 列的 DataFrame
        periods: 均线周期列表

    Returns:
        添加了成交量均线列的 DataFrame
    """
    if periods is None:
        periods = [5, 10, 20]

    df = df.copy()
    for p in periods:
        df[f"VOL_MA{p}"] = ta.sma(df["volume"], length=p)
    return df


def calc_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    计算所有技术指标

    Args:
        df: 包含 OHLCV 数据的 DataFrame

    Returns:
        添加了所有技术指标列的 DataFrame
    """
    if df.empty:
        return df

    df = calc_ma(df)
    df = calc_macd(df)
    df = calc_kdj(df)
    df = calc_rsi(df)
    df = calc_volume_ma(df)
    return df


def get_indicator_signals(df: pd.DataFrame) -> dict:
    """
    根据最新数据生成技术指标信号

    Args:
        df: 包含技术指标的 DataFrame

    Returns:
        信号字典，包含各指标的多空判断
    """
    if df.empty or len(df) < 2:
        return {}

    latest = df.iloc[-1]
    prev = df.iloc[-2]
    signals = {}

    # MACD 信号
    if "MACD_DIF" in df.columns and "MACD_SIGNAL" in df.columns:
        if pd.notna(latest["MACD_DIF"]) and pd.notna(latest["MACD_SIGNAL"]):
            if latest["MACD_DIF"] > latest["MACD_SIGNAL"]:
                signals["MACD"] = "看多 🟢"
            else:
                signals["MACD"] = "看空 🔴"
            # 金叉死叉
            if prev["MACD_DIF"] <= prev["MACD_SIGNAL"] and latest["MACD_DIF"] > latest["MACD_SIGNAL"]:
                signals["MACD_事件"] = "金叉 ⚡"
            elif prev["MACD_DIF"] >= prev["MACD_SIGNAL"] and latest["MACD_DIF"] < latest["MACD_SIGNAL"]:
                signals["MACD_事件"] = "死叉 ⚡"

    # KDJ 信号
    if "K" in df.columns and "D" in df.columns:
        if pd.notna(latest["K"]) and pd.notna(latest["D"]):
            if latest["K"] > latest["D"] and latest["K"] < 80:
                signals["KDJ"] = "看多 🟢"
            elif latest["K"] < latest["D"] and latest["K"] > 20:
                signals["KDJ"] = "看空 🔴"
            elif latest["K"] >= 80:
                signals["KDJ"] = "超买 ⚠️"
            elif latest["K"] <= 20:
                signals["KDJ"] = "超卖 ⚠️"

    # RSI 信号
    if "RSI" in df.columns:
        if pd.notna(latest["RSI"]):
            if latest["RSI"] > 70:
                signals["RSI"] = "超买 ⚠️"
            elif latest["RSI"] < 30:
                signals["RSI"] = "超卖 ⚠️"
            elif latest["RSI"] > 50:
                signals["RSI"] = "偏多 🟢"
            else:
                signals["RSI"] = "偏空 🔴"

    # 均线信号
    if "MA5" in df.columns and "MA20" in df.columns:
        if pd.notna(latest["MA5"]) and pd.notna(latest["MA20"]):
            if latest["MA5"] > latest["MA20"]:
                signals["均线"] = "多头排列 🟢"
            else:
                signals["均线"] = "空头排列 🔴"

    return signals
