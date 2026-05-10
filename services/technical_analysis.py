"""
技术指标计算服务
使用 ta 库计算各类技术指标
"""
import pandas as pd
import numpy as np
from ta.trend import SMAIndicator, MACD
from ta.momentum import StochRSIIndicator, RSIIndicator, StochasticOscillator
from config import MACD_FAST, MACD_SLOW, MACD_SIGNAL, KDJ_PERIOD, RSI_PERIOD, MA_PERIODS


def calc_ma(df: pd.DataFrame, periods: list = None) -> pd.DataFrame:
    if periods is None:
        periods = MA_PERIODS
    df = df.copy()
    for p in periods:
        df[f"MA{p}"] = df["close"].rolling(window=p).mean()
    return df


def calc_macd(
    df: pd.DataFrame,
    fast: int = MACD_FAST,
    slow: int = MACD_SLOW,
    signal: int = MACD_SIGNAL,
) -> pd.DataFrame:
    df = df.copy()
    macd_ind = MACD(close=df["close"], window_slow=slow, window_fast=fast, window_sign=signal)
    df["MACD_DIF"] = macd_ind.macd()
    df["MACD_SIGNAL"] = macd_ind.macd_signal()
    df["MACD_HIST"] = macd_ind.macd_diff()
    return df


def calc_kdj(
    df: pd.DataFrame,
    period: int = KDJ_PERIOD,
) -> pd.DataFrame:
    df = df.copy()
    stoch = StochasticOscillator(
        high=df["high"], low=df["low"], close=df["close"],
        window=period, smooth_window=3,
    )
    df["K"] = stoch.stoch()
    df["D"] = stoch.stoch_signal()
    df["J"] = 3 * df["K"] - 2 * df["D"]
    return df


def calc_rsi(df: pd.DataFrame, period: int = RSI_PERIOD) -> pd.DataFrame:
    df = df.copy()
    rsi_ind = RSIIndicator(close=df["close"], window=period)
    df["RSI"] = rsi_ind.rsi()
    return df


def calc_volume_ma(df: pd.DataFrame, periods: list = None) -> pd.DataFrame:
    if periods is None:
        periods = [5, 10, 20]
    df = df.copy()
    for p in periods:
        df[f"VOL_MA{p}"] = df["volume"].rolling(window=p).mean()
    return df


def calc_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
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
    """
    signals = {}
    if df.empty or len(df) < 2:
        return signals

    last = df.iloc[-1]
    prev = df.iloc[-2]

    # MACD 信号
    if "MACD_DIF" in df.columns and "MACD_SIGNAL" in df.columns:
        if pd.notna(last["MACD_DIF"]) and pd.notna(last["MACD_SIGNAL"]):
            if prev["MACD_DIF"] <= prev["MACD_SIGNAL"] and last["MACD_DIF"] > last["MACD_SIGNAL"]:
                signals["MACD"] = "🟢 金叉（看多）"
            elif prev["MACD_DIF"] >= prev["MACD_SIGNAL"] and last["MACD_DIF"] < last["MACD_SIGNAL"]:
                signals["MACD"] = "🔴 死叉（看空）"
            elif last["MACD_HIST"] > 0:
                signals["MACD"] = "🟢 多头运行"
            else:
                signals["MACD"] = "🔴 空头运行"

    # KDJ 信号
    if "K" in df.columns and "D" in df.columns:
        if pd.notna(last["K"]) and pd.notna(last["D"]):
            if last["K"] > 80 and last["D"] > 80:
                signals["KDJ"] = "🔴 超买区域"
            elif last["K"] < 20 and last["D"] < 20:
                signals["KDJ"] = "🟢 超卖区域"
            elif prev["K"] <= prev["D"] and last["K"] > last["D"]:
                signals["KDJ"] = "🟢 金叉（看多）"
            elif prev["K"] >= prev["D"] and last["K"] < last["D"]:
                signals["KDJ"] = "🔴 死叉（看空）"
            else:
                signals["KDJ"] = "⚪ 震荡"

    # RSI 信号
    if "RSI" in df.columns:
        if pd.notna(last["RSI"]):
            if last["RSI"] > 70:
                signals["RSI"] = "🔴 超买"
            elif last["RSI"] < 30:
                signals["RSI"] = "🟢 超卖"
            else:
                signals["RSI"] = "⚪ 正常区间"

    # 均线信号
    ma_cols = [f"MA{p}" for p in MA_PERIODS if f"MA{p}" in df.columns]
    if ma_cols:
        ma_vals = {col: last[col] for col in ma_cols if pd.notna(last[col])}
        if len(ma_vals) >= 2:
            sorted_mas = sorted(ma_vals.items(), key=lambda x: int(x[0][2:]))
            is_bullish = all(sorted_mas[i][1] > sorted_mas[i + 1][1] for i in range(len(sorted_mas) - 1))
            is_bearish = all(sorted_mas[i][1] < sorted_mas[i + 1][1] for i in range(len(sorted_mas) - 1))
            if is_bullish:
                signals["均线"] = "🟢 多头排列"
            elif is_bearish:
                signals["均线"] = "🔴 空头排列"
            else:
                signals["均线"] = "⚪ 交叉缠绕"

    return signals
