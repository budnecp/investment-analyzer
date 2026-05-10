"""
图表绘制工具
使用 Plotly 绘制K线图和技术指标
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from config import MA_PERIODS


def create_kline_chart(
    df: pd.DataFrame,
    title: str = "K线图",
    show_ma: bool = True,
    ma_periods: list = None,
    show_volume: bool = True,
) -> go.Figure:
    """
    创建K线图

    Args:
        df: 包含 OHLCV 数据的 DataFrame
        title: 图表标题
        show_ma: 是否显示均线
        ma_periods: 均线周期列表
        show_volume: 是否显示成交量

    Returns:
        Plotly Figure 对象
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="暂无数据", xref="paper", yref="paper",
                           x=0.5, y=0.5, showarrow=False, font=dict(size=24))
        return fig

    if ma_periods is None:
        ma_periods = MA_PERIODS

    # 创建子图
    rows = 2 if show_volume else 1
    row_heights = [0.75, 0.25] if show_volume else [1.0]
    subplot_titles = ("",) if show_volume else ()

    fig = make_subplots(
        rows=rows, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=row_heights,
    )

    # K线图
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name="K线",
            increasing_line_color="#ef5350",
            decreasing_line_color="#26a69a",
            increasing_fillcolor="#ef5350",
            decreasing_fillcolor="#26a69a",
        ),
        row=1, col=1,
    )

    # 均线
    if show_ma:
        ma_colors = {
            5: "#ffd54f",
            10: "#ff9800",
            20: "#e91e63",
            60: "#2196f3",
            120: "#9c27b0",
            250: "#795548",
        }
        for p in ma_periods:
            col_name = f"MA{p}"
            if col_name in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df[col_name],
                        mode="lines",
                        name=f"MA{p}",
                        line=dict(
                            color=ma_colors.get(p, "#999999"),
                            width=1,
                        ),
                    ),
                    row=1, col=1,
                )

    # 成交量
    if show_volume and "volume" in df.columns:
        colors = [
            "#ef5350" if df["close"].iloc[i] >= df["open"].iloc[i] else "#26a69a"
            for i in range(len(df))
        ]
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df["volume"],
                name="成交量",
                marker_color=colors,
                opacity=0.7,
            ),
            row=2, col=1,
        )

    # 布局
    fig.update_layout(
        title=dict(text=title, x=0.5, font=dict(size=16)),
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        height=700,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        margin=dict(l=50, r=50, t=80, b=50),
    )

    fig.update_xaxes(title_text="日期", row=rows, col=1)
    fig.update_yaxes(title_text="价格", row=1, col=1)
    if show_volume:
        fig.update_yaxes(title_text="成交量", row=2, col=1)

    return fig


def create_macd_chart(df: pd.DataFrame, title: str = "MACD") -> go.Figure:
    """
    创建 MACD 图表

    Args:
        df: 包含 MACD_DIF, MACD_SIGNAL, MACD_HIST 列的 DataFrame
        title: 图表标题

    Returns:
        Plotly Figure 对象
    """
    fig = make_subplots(rows=1, cols=1)

    if "MACD_DIF" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df["MACD_DIF"],
                mode="lines", name="DIF",
                line=dict(color="#2196f3", width=1.5),
            )
        )

    if "MACD_SIGNAL" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df["MACD_SIGNAL"],
                mode="lines", name="DEA",
                line=dict(color="#ff9800", width=1.5),
            )
        )

    if "MACD_HIST" in df.columns:
        colors = [
            "#ef5350" if v >= 0 else "#26a69a"
            for v in df["MACD_HIST"].fillna(0)
        ]
        fig.add_trace(
            go.Bar(
                x=df.index, y=df["MACD_HIST"],
                name="MACD柱",
                marker_color=colors,
                opacity=0.7,
            )
        )

    fig.update_layout(
        title=dict(text=title, x=0.5),
        template="plotly_dark",
        height=300,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=50, r=50, t=50, b=30),
    )
    fig.update_yaxes(title_text="MACD")

    return fig


def create_kdj_chart(df: pd.DataFrame, title: str = "KDJ") -> go.Figure:
    """
    创建 KDJ 图表

    Args:
        df: 包含 K, D, J 列的 DataFrame
        title: 图表标题

    Returns:
        Plotly Figure 对象
    """
    fig = go.Figure()

    if "K" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df["K"],
                mode="lines", name="K",
                line=dict(color="#2196f3", width=1.5),
            )
        )

    if "D" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df["D"],
                mode="lines", name="D",
                line=dict(color="#ff9800", width=1.5),
            )
        )

    if "J" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df["J"],
                mode="lines", name="J",
                line=dict(color="#e91e63", width=1.5),
            )
        )

    # 超买超卖区域
    fig.add_hline(y=80, line_dash="dash", line_color="rgba(255,0,0,0.3)", annotation_text="超买")
    fig.add_hline(y=20, line_dash="dash", line_color="rgba(0,255,0,0.3)", annotation_text="超卖")

    fig.update_layout(
        title=dict(text=title, x=0.5),
        template="plotly_dark",
        height=300,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=50, r=50, t=50, b=30),
    )
    fig.update_yaxes(title_text="KDJ")

    return fig


def create_rsi_chart(df: pd.DataFrame, title: str = "RSI") -> go.Figure:
    """
    创建 RSI 图表

    Args:
        df: 包含 RSI 列的 DataFrame
        title: 图表标题

    Returns:
        Plotly Figure 对象
    """
    fig = go.Figure()

    if "RSI" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df["RSI"],
                mode="lines", name="RSI",
                line=dict(color="#9c27b0", width=1.5),
            )
        )

    # 超买超卖区域
    fig.add_hline(y=70, line_dash="dash", line_color="rgba(255,0,0,0.3)", annotation_text="超买(70)")
    fig.add_hline(y=30, line_dash="dash", line_color="rgba(0,255,0,0.3)", annotation_text="超卖(30)")
    fig.add_hrect(y0=30, y1=70, fillcolor="rgba(128,128,128,0.1)", line_width=0)

    fig.update_layout(
        title=dict(text=title, x=0.5),
        template="plotly_dark",
        height=300,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=50, r=50, t=50, b=30),
    )
    fig.update_yaxes(title_text="RSI")

    return fig


def create_kline_with_chan(
    df: pd.DataFrame,
    chan_result: dict,
    title: str = "缠论分析",
) -> go.Figure:
    """
    创建带缠论标注的K线图

    Args:
        df: 包含 OHLCV 数据的 DataFrame
        chan_result: 缠论分析结果
        title: 图表标题

    Returns:
        Plotly Figure 对象
    """
    # 基础K线图
    fig = create_kline_chart(df, title=title, show_ma=False, show_volume=False)

    # 标注分型
    fractals = chan_result.get("fractals", pd.DataFrame())
    if not fractals.empty:
        # 顶分型
        top_fractals = fractals[fractals["fractal_type"] == 1]
        if not top_fractals.empty:
            fig.add_trace(
                go.Scatter(
                    x=top_fractals.index,
                    y=top_fractals["high"] * 1.005,
                    mode="markers",
                    name="顶分型",
                    marker=dict(symbol="triangle-down", size=10, color="#ff5722"),
                )
            )

        # 底分型
        bottom_fractals = fractals[fractals["fractal_type"] == -1]
        if not bottom_fractals.empty:
            fig.add_trace(
                go.Scatter(
                    x=bottom_fractals.index,
                    y=bottom_fractals["low"] * 0.995,
                    mode="markers",
                    name="底分型",
                    marker=dict(symbol="triangle-up", size=10, color="#4caf50"),
                )
            )

    # 标注笔
    bi_list = chan_result.get("bi", [])
    for bi in bi_list:
        start_idx, end_idx, direction = bi
        if start_idx < len(df) and end_idx < len(df):
            fig.add_shape(
                type="line",
                x0=df.index[start_idx],
                x1=df.index[end_idx],
                y0=df["low"].iloc[start_idx] if direction == 1 else df["high"].iloc[start_idx],
                y1=df["high"].iloc[end_idx] if direction == 1 else df["low"].iloc[end_idx],
                line=dict(color="#ffeb3b", width=2, dash="dot"),
            )

    return fig


def create_kline_with_elliott(
    df: pd.DataFrame,
    elliott_result: dict,
    title: str = "波浪理论分析",
) -> go.Figure:
    """
    创建带波浪标注的K线图

    Args:
        df: 包含 OHLCV 数据的 DataFrame
        elliott_result: 波浪分析结果
        title: 图表标题

    Returns:
        Plotly Figure 对象
    """
    fig = create_kline_chart(df, title=title, show_ma=False, show_volume=False)

    # 标注推动浪
    impulse_waves = elliott_result.get("impulse_waves", [])
    wave_colors_impulse = ["#4caf50", "#ff9800", "#2196f3", "#9c27b0", "#f44336"]

    for wave in impulse_waves[-3:]:  # 只显示最近的3个
        points = wave["points"]
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]
            fig.add_shape(
                type="line",
                x0=p1[0], x1=p2[0],
                y0=p1[1], y1=p2[1],
                line=dict(
                    color=wave_colors_impulse[i % 5],
                    width=2.5,
                ),
            )
            # 标注浪号
            fig.add_annotation(
                x=p1[0],
                y=p1[1],
                text=f"W{i + 1}",
                showarrow=False,
                font=dict(size=12, color=wave_colors_impulse[i % 5]),
            )

    # 标注调整浪
    corrective_waves = elliott_result.get("corrective_waves", [])
    wave_colors_corrective = ["#e91e63", "#00bcd4", "#e91e63"]

    for wave in corrective_waves[-2:]:  # 只显示最近的2个
        points = wave["points"]
        labels = ["A", "B", "C"]
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]
            fig.add_shape(
                type="line",
                x0=p1[0], x1=p2[0],
                y0=p1[1], y1=p2[1],
                line=dict(
                    color=wave_colors_corrective[i % 3],
                    width=2,
                    dash="dash",
                ),
            )
            fig.add_annotation(
                x=p1[0],
                y=p1[1],
                text=labels[i],
                showarrow=False,
                font=dict(size=12, color=wave_colors_corrective[i % 3]),
            )

    return fig
