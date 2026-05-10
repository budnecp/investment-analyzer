"""
缠论分析模块 - 基础笔段划分算法
实现缠论的核心概念：分型、笔、线段
"""
import pandas as pd
import numpy as np
from config import CHAN_MIN_BARS


def find_fractals(df: pd.DataFrame) -> pd.DataFrame:
    """
    识别顶分型和底分型

    缠论定义：
    - 顶分型：第二根K线的高点最高，且三根K线的高点呈"中间高两边低"
    - 底分型：第二根K线的低点最低，且三根K线的低点呈"中间低两边高"

    Args:
        df: 包含 high, low 列的 DataFrame

    Returns:
        添加了 fractal_type 列的 DataFrame（1=顶分型, -1=底分型, 0=无）
    """
    df = df.copy()
    df["fractal_type"] = 0

    for i in range(1, len(df) - 1):
        # 顶分型判断
        if (df["high"].iloc[i] > df["high"].iloc[i - 1] and
                df["high"].iloc[i] > df["high"].iloc[i + 1] and
                df["low"].iloc[i] > df["low"].iloc[i - 1] and
                df["low"].iloc[i] > df["low"].iloc[i + 1]):
            df.iloc[i, df.columns.get_loc("fractal_type")] = 1

        # 底分型判断
        elif (df["low"].iloc[i] < df["low"].iloc[i - 1] and
              df["low"].iloc[i] < df["low"].iloc[i + 1] and
              df["high"].iloc[i] < df["high"].iloc[i - 1] and
              df["high"].iloc[i] < df["high"].iloc[i + 1]):
            df.iloc[i, df.columns.get_loc("fractal_type")] = -1

    return df


def merge_inclusive_klines(df: pd.DataFrame) -> pd.DataFrame:
    """
    处理K线包含关系

    缠论要求：相邻K线如果存在包含关系（一根K线的高低点完全包含另一根），
    需要合并处理。

    合并规则：
    - 向上趋势中，取两根K线的高点最高值和低点最高值
    - 向下趋势中，取两根K线的高点最低值和低点最低值

    Args:
        df: 包含 high, low, open, close 列的 DataFrame

    Returns:
        合并处理后的 DataFrame
    """
    if len(df) < 2:
        return df

    merged = df.copy()
    to_drop = []

    i = 1
    while i < len(merged):
        prev = merged.iloc[i - 1]
        curr = merged.iloc[i]

        # 判断包含关系
        is_inclusive = (
            (curr["high"] <= prev["high"] and curr["low"] >= prev["low"]) or
            (prev["high"] <= curr["high"] and prev["low"] >= curr["low"])
        )

        if is_inclusive:
            # 判断趋势方向
            if i >= 2:
                prev_prev = merged.iloc[i - 2]
                direction = 1 if prev["high"] > prev_prev["high"] else -1
            else:
                direction = 1 if curr["close"] > prev["close"] else -1

            # 合并
            if direction == 1:
                # 向上：取高高、高低
                merged.iloc[i - 1, merged.columns.get_loc("high")] = max(prev["high"], curr["high"])
                merged.iloc[i - 1, merged.columns.get_loc("low")] = max(prev["low"], curr["low"])
            else:
                # 向下：取低高、低低
                merged.iloc[i - 1, merged.columns.get_loc("high")] = min(prev["high"], curr["high"])
                merged.iloc[i - 1, merged.columns.get_loc("low")] = min(prev["low"], curr["low"])

            to_drop.append(i)
            i += 1
        else:
            i += 1

    if to_drop:
        merged = merged.drop(merged.index[to_drop]).reset_index(drop=True)

    return merged


def find_bi(df: pd.DataFrame, min_bars: int = CHAN_MIN_BARS) -> list:
    """
    识别笔

    缠论定义：笔是由相邻的顶分型和底分型连接而成。
    要求顶底分型之间至少有 min_bars 根K线（处理包含关系后）。

    Args:
        df: 包含 fractal_type 列的 DataFrame
        min_bars: 顶底分型之间的最少K线数

    Returns:
        笔的列表，每个元素为 (start_idx, end_idx, direction)
        direction: 1=向上笔, -1=向下笔
    """
    fractals = df[df["fractal_type"] != 0].copy()

    if len(fractals) < 2:
        return []

    bi_list = []
    last_fractal_idx = fractals.index[0]
    last_fractal_type = fractals.iloc[0]["fractal_type"]

    for i in range(1, len(fractals)):
        curr_idx = fractals.index[i]
        curr_type = fractals.iloc[i]["fractal_type"]

        # 顶底交替，且间距足够
        if (curr_type != last_fractal_type and
                curr_idx - last_fractal_idx >= min_bars):
            direction = 1 if last_fractal_type == -1 else -1
            bi_list.append((last_fractal_idx, curr_idx, direction))
            last_fractal_idx = curr_idx
            last_fractal_type = curr_type
        else:
            # 同类型分型，取更极端的
            if last_fractal_type == 1 and curr_type == 1:
                if df["high"].iloc[curr_idx] > df["high"].iloc[last_fractal_idx]:
                    last_fractal_idx = curr_idx
            elif last_fractal_type == -1 and curr_type == -1:
                if df["low"].iloc[curr_idx] < df["low"].iloc[last_fractal_idx]:
                    last_fractal_idx = curr_idx

    return bi_list


def find_duan(df: pd.DataFrame, bi_list: list) -> list:
    """
    识别线段

    缠论定义：线段由至少3笔组成。
    当相邻笔的高低点出现特征序列破坏时，线段结束。

    当前为基础实现，后续迭代完善。

    Args:
        df: 原始 DataFrame
        bi_list: 笔的列表

    Returns:
        线段列表，每个元素为 (start_idx, end_idx)
    """
    if len(bi_list) < 3:
        return []

    duan_list = []
    start_idx = bi_list[0][0]

    for i in range(2, len(bi_list)):
        # 简化判断：如果第3笔破坏了第1笔的极值点，形成新线段
        bi1 = bi_list[i - 2]
        bi2 = bi_list[i - 1]
        bi3 = bi_list[i]

        if bi1[2] == 1:  # 第一笔向上
            # 向上线段，如果第3笔低点低于第1笔高点
            if df["low"].iloc[bi3[1]] < df["low"].iloc[bi1[1]]:
                duan_list.append((start_idx, bi2[1]))
                start_idx = bi2[1]
        else:  # 第一笔向下
            # 向下线段，如果第3笔高点高于第1笔低点
            if df["high"].iloc[bi3[1]] > df["high"].iloc[bi1[1]]:
                duan_list.append((start_idx, bi2[1]))
                start_idx = bi2[1]

    # 添加最后一个线段
    if start_idx != bi_list[-1][1]:
        duan_list.append((start_idx, bi_list[-1][1]))

    return duan_list


def analyze_chan(df: pd.DataFrame) -> dict:
    """
    执行完整的缠论分析

    Args:
        df: 包含 OHLCV 数据的 DataFrame

    Returns:
        缠论分析结果字典
    """
    if df.empty or len(df) < 5:
        return {"fractals": pd.DataFrame(), "bi": [], "duan": []}

    # 1. 处理包含关系
    merged = merge_inclusive_klines(df)

    # 2. 识别分型
    merged = find_fractals(merged)

    # 3. 识别笔
    bi_list = find_bi(merged)

    # 4. 识别线段
    duan_list = find_duan(merged, bi_list)

    # 在原始df上标注分型
    df_marked = find_fractals(df)

    return {
        "fractals": df_marked[df_marked["fractal_type"] != 0],
        "bi": bi_list,
        "duan": duan_list,
        "merged_df": merged,
    }
