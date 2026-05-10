"""
📈 技术分析页面
- MACD/KDJ/RSI/成交量指标
- 均线系统 MA5/MA10/MA20/MA60/MA120/MA250
- 缠论基础分析
- 波浪理论基础分析
"""
import streamlit as st
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DEFAULT_SYMBOLS, FUTURES_SYMBOLS, KLINE_PERIODS, MA_PERIODS
from services.market_data import get_kline_data, resolve_symbol
from services.technical_analysis import calc_all_indicators, get_indicator_signals
from services.chan_theory import analyze_chan
from services.elliott_wave import analyze_elliott
from utils.chart_helper import (
    create_kline_chart,
    create_macd_chart,
    create_kdj_chart,
    create_rsi_chart,
    create_kline_with_chan,
    create_kline_with_elliott,
)

st.set_page_config(
    page_title="技术分析",
    page_icon="📈",
    layout="wide",
)


def get_all_symbols() -> dict:
    """获取所有可用品种"""
    symbols = dict(DEFAULT_SYMBOLS)
    symbols.update(FUTURES_SYMBOLS)
    # 添加自定义品种
    if "custom_symbols" in st.session_state:
        symbols.update(st.session_state.custom_symbols)
    return symbols


def display_technical_indicators(df: pd.DataFrame, symbol_name: str):
    """展示技术指标"""
    st.subheader("📉 技术指标")

    # 指标信号汇总
    signals = get_indicator_signals(df)
    if signals:
        st.markdown("##### 🎯 信号汇总")
        signal_cols = st.columns(len(signals))
        for i, (key, value) in enumerate(signals.items()):
            with signal_cols[i]:
                label = key.replace("_", " ")
                st.metric(label=label, value=value)

    # 指标选择
    tab_macd, tab_kdj, tab_rsi = st.tabs(["MACD", "KDJ", "RSI"])

    with tab_macd:
        fig_macd = create_macd_chart(df, title=f"{symbol_name} - MACD")
        st.plotly_chart(fig_macd, use_container_width=True)

        # MACD 解读
        with st.expander("📖 MACD 解读"):
            if "MACD_DIF" in df.columns and len(df) >= 2:
                latest = df.iloc[-1]
                prev = df.iloc[-2]
                dif = latest["MACD_DIF"]
                dea = latest["MACD_SIGNAL"]
                hist = latest["MACD_HIST"]

                st.markdown(f"""
                **当前状态：**
                - DIF: `{dif:.4f}`
                - DEA: `{dea:.4f}`
                - MACD柱: `{hist:.4f}`

                **判断依据：**
                - DIF > DEA → 多头信号 🟢
                - DIF < DEA → 空头信号 🔴
                - MACD柱由负转正 → 金叉买入信号
                - MACD柱由正转负 → 死叉卖出信号
                """)

    with tab_kdj:
        fig_kdj = create_kdj_chart(df, title=f"{symbol_name} - KDJ")
        st.plotly_chart(fig_kdj, use_container_width=True)

        with st.expander("📖 KDJ 解读"):
            if "K" in df.columns:
                latest = df.iloc[-1]
                st.markdown(f"""
                **当前状态：**
                - K值: `{latest['K']:.2f}`
                - D值: `{latest['D']:.2f}`
                - J值: `{latest['J']:.2f}`

                **判断依据：**
                - K > 80 且 D > 80 → 超买区域 ⚠️
                - K < 20 且 D < 20 → 超卖区域 ⚠️
                - K线上穿D线 → 买入信号
                - K线下穿D线 → 卖出信号
                - J值 > 100 或 < 0 → 极端区域
                """)

    with tab_rsi:
        fig_rsi = create_rsi_chart(df, title=f"{symbol_name} - RSI")
        st.plotly_chart(fig_rsi, use_container_width=True)

        with st.expander("📖 RSI 解读"):
            if "RSI" in df.columns:
                latest = df.iloc[-1]
                rsi_val = latest["RSI"]
                st.markdown(f"""
                **当前 RSI: `{rsi_val:.2f}`**

                **判断依据：**
                - RSI > 70 → 超买区域，可能回调 ⚠️
                - RSI < 30 → 超卖区域，可能反弹 ⚠️
                - RSI 50 为多空分界线
                - RSI 背离是重要的趋势反转信号
                """)


def display_ma_system(df: pd.DataFrame, symbol_name: str):
    """展示均线系统"""
    st.subheader("📏 均线系统")

    # 均线K线图
    fig = create_kline_chart(
        df,
        title=f"{symbol_name} - 均线系统",
        show_ma=True,
        show_volume=True,
    )
    st.plotly_chart(fig, use_container_width=True)

    # 均线数据
    with st.expander("📋 均线数据"):
        ma_cols = [f"MA{p}" for p in MA_PERIODS if f"MA{p}" in df.columns]
        if ma_cols:
            latest = df.iloc[-1]
            close = latest["close"]

            ma_data = []
            for col in ma_cols:
                ma_val = latest[col]
                if pd.notna(ma_val):
                    diff = ((close - ma_val) / ma_val) * 100
                    ma_data.append({
                        "均线": col,
                        "数值": f"${ma_val:,.2f}",
                        "偏离度": f"{diff:+.2f}%",
                        "趋势": "上方 🟢" if close > ma_val else "下方 🔴",
                    })

            if ma_data:
                st.dataframe(
                    pd.DataFrame(ma_data),
                    use_container_width=True,
                    hide_index=True,
                )

    # 均线排列判断
    with st.expander("📖 均线系统解读"):
        ma_vals = {}
        for p in MA_PERIODS:
            col = f"MA{p}"
            if col in df.columns and pd.notna(df.iloc[-1][col]):
                ma_vals[p] = df.iloc[-1][col]

        if len(ma_vals) >= 3:
            sorted_mas = sorted(ma_vals.items(), key=lambda x: x[1], reverse=True)
            order = [f"MA{p}" for p, _ in sorted_mas]

            if order == [f"MA{p}" for p in sorted(ma_vals.keys())]:
                st.success("多头排列：短期均线在上，长期均线在下，趋势向好 🟢")
            elif order == [f"MA{p}" for p in sorted(ma_vals.keys(), reverse=True)]:
                st.error("空头排列：长期均线在上，短期均线在下，趋势偏弱 🔴")
            else:
                st.warning("均线交叉缠绕，方向不明确 🟡")


def display_chan_theory(df: pd.DataFrame, symbol_name: str):
    """展示缠论分析"""
    st.subheader("🔮 缠论分析")

    with st.spinner("正在执行缠论分析..."):
        chan_result = analyze_chan(df)

    # 缠论K线图
    fig_chan = create_kline_with_chan(df, chan_result, title=f"{symbol_name} - 缠论笔段")
    st.plotly_chart(fig_chan, use_container_width=True)

    # 分析结果
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### 📊 分型统计")
        fractals = chan_result.get("fractals", pd.DataFrame())
        if not fractals.empty:
            top_count = len(fractals[fractals["fractal_type"] == 1])
            bottom_count = len(fractals[fractals["fractal_type"] == -1])
            st.write(f"- 顶分型数量：**{top_count}**")
            st.write(f"- 底分型数量：**{bottom_count}**")
        else:
            st.info("未识别到分型")

    with col2:
        st.markdown("##### 📈 笔段统计")
        bi_list = chan_result.get("bi", [])
        duan_list = chan_result.get("duan", [])
        st.write(f"- 识别笔数：**{len(bi_list)}**")
        st.write(f"- 识别线段数：**{len(duan_list)}**")

        if bi_list:
            last_bi = bi_list[-1]
            direction = "向上 ↗️" if last_bi[2] == 1 else "向下 ↘️"
            st.write(f"- 最新笔方向：**{direction}**")

    # 缠论说明
    with st.expander("📖 缠论基础概念"):
        st.markdown("""
        **缠论核心概念：**

        1. **分型**：三根K线组合中，中间K线高点最高为顶分型，低点最低为底分型
        2. **笔**：相邻的顶底分型连接而成，代表一段趋势
        3. **线段**：至少3笔构成，是更高级别的趋势划分

        **当前实现：**
        - ✅ K线包含关系处理
        - ✅ 顶底分型识别
        - ✅ 笔的划分
        - ✅ 线段的基础识别
        - 🔄 后续迭代：中枢识别、买卖点判断

        > ⚠️ 缠论分析为基础版本，后续会持续完善算法
        """)


def display_elliott_wave(df: pd.DataFrame, symbol_name: str):
    """展示波浪理论分析"""
    st.subheader("🌊 波浪理论分析")

    # 摆动窗口设置
    swing_window = st.slider(
        "摆动点识别窗口",
        min_value=3,
        max_value=20,
        value=5,
        step=1,
        help="较小的窗口识别更多波浪细节，较大的窗口识别主要趋势",
    )

    with st.spinner("正在执行波浪理论分析..."):
        elliott_result = analyze_elliott(df, swing_window=swing_window)

    # 波浪K线图
    fig_elliott = create_kline_with_elliott(df, elliott_result, title=f"{symbol_name} - 波浪理论")
    st.plotly_chart(fig_elliott, use_container_width=True)

    # 分析结果
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### 📈 推动浪识别")
        impulse_waves = elliott_result.get("impulse_waves", [])
        if impulse_waves:
            st.write(f"识别到 **{len(impulse_waves)}** 个推动浪结构")
            # 显示最近的推动浪
            for i, wave in enumerate(impulse_waves[-3:]):
                with st.expander(f"推动浪 #{len(impulse_waves) - 2 + i} - {wave['direction']}"):
                    st.json(wave["wave_sizes"])
                    st.write(f"W2回撤W1: {wave['retracement']['W2/W1']}%")
                    st.write(f"W4回撤W3: {wave['retracement']['W4/W3']}%")
        else:
            st.info("未识别到推动浪结构，可尝试调整摆动窗口大小")

    with col2:
        st.markdown("##### 📉 调整浪识别")
        corrective_waves = elliott_result.get("corrective_waves", [])
        if corrective_waves:
            st.write(f"识别到 **{len(corrective_waves)}** 个调整浪结构")
            for i, wave in enumerate(corrective_waves[-2:]):
                with st.expander(f"调整浪 #{len(corrective_waves) - 1 + i} - {wave['direction']}"):
                    st.json(wave["wave_sizes"])
                    st.write(f"B浪回撤A浪: {wave['b_retracement']}%")
        else:
            st.info("未识别到调整浪结构")

    # 当前浪型判断
    status = elliott_result.get("current_status", {})
    if status:
        st.markdown("##### 🎯 当前浪型判断")
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**当前所处：** {status.get('current_position', '未知')}")
        with col2:
            st.warning(f"**建议：** {status.get('suggestion', '无')}")

    # 波浪理论说明
    with st.expander("📖 波浪理论基础"):
        st.markdown("""
        **Elliott Wave 波浪理论：**

        1. **推动浪（5浪结构）**：
           - 浪1：初始上涨/下跌
           - 浪2：回调（不超过浪1的100%）
           - 浪3：主升/跌浪（不是最短的推动浪）
           - 浪4：回调（不进入浪1区域）
           - 浪5：最后一波推动

        2. **调整浪（3浪结构）**：
           - A浪：第一波调整
           - B浪：反弹（通常回撤A浪的38.2%-78.6%）
           - C浪：第二波调整

        3. **三大铁律**：
           - 浪2不超过浪1起点
           - 浪3不是最短的推动浪
           - 浪4不进入浪1区域

        > ⚠️ 波浪理论分析为基础版本，识别结果仅供参考
        """)


def main():
    st.title("📈 技术分析")
    st.markdown("---")

    # 品种选择
    all_symbols = get_all_symbols()

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        selected_name = st.selectbox(
            "选择品种",
            options=list(all_symbols.keys()),
            format_func=lambda x: f"{x} ({all_symbols[x]})",
        )
    with col2:
        period = st.selectbox(
            "K线周期",
            options=list(KLINE_PERIODS.keys()),
            index=0,
        )
    with col3:
        st.write("")
        st.write("")
        analyze_btn = st.button("🔍 开始分析", type="primary", use_container_width=True)

    if not selected_name:
        st.warning("请选择品种")
        return

    symbol = all_symbols[selected_name]

    # 获取数据
    with st.spinner("正在获取行情数据..."):
        df = get_kline_data(symbol, period)

    if df.empty:
        st.error(f"无法获取 {selected_name} 的数据，请检查品种代码或网络连接")
        return

    # 计算技术指标
    with st.spinner("正在计算技术指标..."):
        df = calc_all_indicators(df)

    # 功能Tab
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 技术指标",
        "📏 均线系统",
        "🔮 缠论分析",
        "🌊 波浪理论",
    ])

    with tab1:
        display_technical_indicators(df, selected_name)

    with tab2:
        display_ma_system(df, selected_name)

    with tab3:
        display_chan_theory(df, selected_name)

    with tab4:
        display_elliott_wave(df, selected_name)


main()
