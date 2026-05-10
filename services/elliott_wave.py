"""
波浪理论分析模块 - Elliott Wave 基础实现
识别推动浪（5浪）和调整浪（3浪）的基本结构
"""
import pandas as pd
import numpy as np
from config import WAVE_MIN_SIZE


def find_swing_points(df: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    """
    识别摆动高低点（Swing Points）

    Args:
        df: 包含 high, low 列的 DataFrame
        window: 识别窗口大小

    Returns:
        添加了 swing_type 列的 DataFrame（1=高点, -1=低点, 0=普通点）
    """
    df = df.copy()
    df["swing_type"] = 0

    for i in range(window, len(df) - window):
        # 检测局部高点
        is_high = True
        for j in range(1, window + 1):
            if df["high"].iloc[i] <= df["high"].iloc[i - j] or \
               df["high"].iloc[i] <= df["high"].iloc[i + j]:
                is_high = False
                break
        if is_high:
            df.iloc[i, df.columns.get_loc("swing_type")] = 1
            continue

        # 检测局部低点
        is_low = True
        for j in range(1, window + 1):
            if df["low"].iloc[i] >= df["low"].iloc[i - j] or \
               df["low"].iloc[i] >= df["low"].iloc[i + j]:
                is_low = False
                break
        if is_low:
            df.iloc[i, df.columns.get_loc("swing_type")] = -1

    return df


def identify_impulse_wave(swing_points: list, min_size: float = WAVE_MIN_SIZE) -> list:
    """
    识别推动浪（Impulse Wave）

    推动浪规则：
    1. 浪2回撤不超过浪1的100%
    2. 浪3不是最短的推动浪
    3. 浪4不进入浪1的价格区域

    Args:
        swing_points: 摆动点列表 [(index, price, type), ...]
        min_size: 最小波浪幅度比例

    Returns:
        识别到的推动浪列表
    """
    if len(swing_points) < 6:
        return []

    waves = []

    # 尝试从每个可能的起点识别5浪结构
    for start in range(len(swing_points) - 5):
        # 选取6个摆动点（5浪需要6个端点）
        points = swing_points[start:start + 6]

        # 验证高低点交替
        valid_alternation = True
        for i in range(1, len(points)):
            if points[i][2] == points[i - 1][2]:
                valid_alternation = False
                break

        if not valid_alternation:
            continue

        # 提取价格
        prices = [p[1] for p in points]

        # 判断是上升5浪还是下降5浪
        is_bullish = points[0][2] == -1  # 起点是低点 -> 上升5浪

        if is_bullish:
            # 上升5浪：低-高-低-高-低-高
            w1 = prices[1] - prices[0]  # 浪1上涨
            w2 = prices[1] - prices[2]  # 浪2回调
            w3 = prices[3] - prices[2]  # 浪3上涨
            w4 = prices[3] - prices[4]  # 浪4回调
            w5 = prices[5] - prices[4]  # 浪5上涨

            # 检查方向
            if w1 <= 0 or w3 <= 0 or w5 <= 0:
                continue
            if w2 <= 0 or w4 <= 0:
                continue
        else:
            # 下降5浪：高-低-高-低-高-低
            w1 = prices[0] - prices[1]  # 浪1下跌
            w2 = prices[2] - prices[1]  # 浪2反弹
            w3 = prices[2] - prices[3]  # 浪3下跌
            w4 = prices[4] - prices[3]  # 浪4反弹
            w5 = prices[4] - prices[5]  # 浪5下跌

            if w1 <= 0 or w3 <= 0 or w5 <= 0:
                continue
            if w2 <= 0 or w4 <= 0:
                continue

        # 规则1：浪2回撤不超过浪1的100%
        if w2 / w1 > 1.0:
            continue

        # 规则2：浪3不是最短的
        if w3 < w1 and w3 < w5:
            continue

        # 规则3：浪4不进入浪1区域
        if is_bullish:
            if prices[4] < prices[1]:  # 浪4低点低于浪1高点
                continue
        else:
            if prices[4] > prices[1]:  # 浪4高点高于浪1低点
                continue

        # 检查最小幅度
        total_range = abs(prices[-1] - prices[0])
        if total_range / prices[0] < min_size:
            continue

        wave_info = {
            "type": "Impulse" if is_bullish else "Impulse (Down)",
            "direction": "上升" if is_bullish else "下降",
            "start_idx": points[0][0],
            "end_idx": points[-1][0],
            "points": points,
            "wave_sizes": {
                "W1": round(w1, 2),
                "W2": round(w2, 2),
                "W3": round(w3, 2),
                "W4": round(w4, 2),
                "W5": round(w5, 2),
            },
            "retracement": {
                "W2/W1": round(w2 / w1 * 100, 1),
                "W4/W3": round(w4 / w3 * 100, 1),
            },
        }
        waves.append(wave_info)

    return waves


def identify_corrective_wave(swing_points: list, min_size: float = WAVE_MIN_SIZE) -> list:
    """
    识别调整浪（Corrective Wave）

    调整浪基本模式：A-B-C（3浪结构）

    Args:
        swing_points: 摆动点列表
        min_size: 最小波浪幅度比例

    Returns:
        识别到的调整浪列表
    """
    if len(swing_points) < 4:
        return []

    waves = []

    for start in range(len(swing_points) - 3):
        points = swing_points[start:start + 4]
        prices = [p[1] for p in points]

        # 验证高低点交替
        valid = True
        for i in range(1, len(points)):
            if points[i][2] == points[i - 1][2]:
                valid = False
                break
        if not valid:
            continue

        # 判断调整浪方向
        is_zigzag = points[0][2] == 1  # 起点是高点 -> 之字形调整

        if is_zigzag:
            wa = prices[0] - prices[1]  # A浪下跌
            wb = prices[2] - prices[1]  # B浪反弹
            wc = prices[2] - prices[3]  # C浪下跌

            if wa <= 0 or wc <= 0:
                continue
            if wb <= 0:
                continue
        else:
            wa = prices[1] - prices[0]  # A浪上涨
            wb = prices[1] - prices[2]  # B浪回调
            wc = prices[3] - prices[2]  # C浪上涨

            if wa <= 0 or wc <= 0:
                continue
            if wb <= 0:
                continue

        # B浪回撤通常在38.2%-78.6%之间
        b_retracement = wb / wa
        if b_retracement < 0.236 or b_retracement > 1.0:
            continue

        total_range = abs(prices[-1] - prices[0])
        if total_range / prices[0] < min_size:
            continue

        wave_info = {
            "type": "Zigzag" if is_zigzag else "Zigzag (Up)",
            "direction": "之字形调整" if is_zigzag else "倒之字形调整",
            "start_idx": points[0][0],
            "end_idx": points[-1][0],
            "points": points,
            "wave_sizes": {
                "A": round(wa, 2),
                "B": round(wb, 2),
                "C": round(wc, 2),
            },
            "b_retracement": round(b_retracement * 100, 1),
        }
        waves.append(wave_info)

    return waves


def analyze_elliott(df: pd.DataFrame, swing_window: int = 5) -> dict:
    """
    执行完整的波浪理论分析

    Args:
        df: 包含 OHLCV 数据的 DataFrame
        swing_window: 摆动点识别窗口

    Returns:
        波浪分析结果字典
    """
    if df.empty or len(df) < swing_window * 2 + 1:
        return {"impulse_waves": [], "corrective_waves": [], "swing_df": pd.DataFrame()}

    # 1. 识别摆动点
    swing_df = find_swing_points(df, window=swing_window)

    # 2. 提取摆动点列表
    swing_points = []
    for idx, row in swing_df[swing_df["swing_type"] != 0].iterrows():
        if row["swing_type"] == 1:
            swing_points.append((idx, row["high"], 1))
        else:
            swing_points.append((idx, row["low"], -1))

    # 3. 识别推动浪
    impulse_waves = identify_impulse_wave(swing_points)

    # 4. 识别调整浪
    corrective_waves = identify_corrective_wave(swing_points)

    # 5. 获取当前可能的浪型判断
    current_wave_status = _get_current_wave_status(impulse_waves, corrective_waves)

    return {
        "impulse_waves": impulse_waves,
        "corrective_waves": corrective_waves,
        "swing_df": swing_df,
        "current_status": current_wave_status,
    }


def _get_current_wave_status(impulse_waves: list, corrective_waves: list) -> dict:
    """
    判断当前可能所处的浪型

    Args:
        impulse_waves: 推动浪列表
        corrective_waves: 调整浪列表

    Returns:
        当前浪型状态
    """
    status = {
        "latest_impulse": None,
        "latest_corrective": None,
        "current_position": "未知",
        "suggestion": "数据不足，无法判断",
    }

    if impulse_waves:
        latest = impulse_waves[-1]
        status["latest_impulse"] = latest
        status["current_position"] = f"推动浪中（{latest['direction']}方向）"

        sizes = latest["wave_sizes"]
        if "W5" in sizes:
            status["suggestion"] = "推动浪5浪可能完成，关注调整浪开始"

    if corrective_waves:
        latest = corrective_waves[-1]
        status["latest_corrective"] = latest
        if not impulse_waves:
            status["current_position"] = f"调整浪中（{latest['direction']}）"
            status["suggestion"] = "调整浪进行中，等待完成信号"

    return status
