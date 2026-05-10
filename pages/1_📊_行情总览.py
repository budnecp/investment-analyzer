"""
📊 行情总览页面
- 贵金属实时价格展示
- K线走势图（日K/周K/月K可切换）
- 自定义期货品种添加/删除
"""
import streamlit as st
import sys
import os

# 添加项目根目录到 sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DEFAULT_SYMBOLS, FUTURES_SYMBOLS, KLINE_PERIODS
from services.market_data import get_kline_data, get_realtime_price, get_all_default_prices, get_custom_futures_prices, resolve_symbol
from utils.chart_helper import create_kline_chart

st.set_page_config(
    page_title="行情总览",
    page_icon="📊",
    layout="wide",
)


def init_session_state():
    """初始化 session_state"""
    if "custom_symbols" not in st.session_state:
        st.session_state.custom_symbols = {}


def display_price_cards(prices: dict, title: str):
    """展示价格卡片"""
    st.subheader(title)
    cols = st.columns(len(prices))
    for i, (name, info) in enumerate(prices.items()):
        with cols[i]:
            price = info.get("price", 0)
            change = info.get("change", 0)
            change_pct = info.get("change_pct", 0)

            if "error" in info:
                st.metric(label=name, value="获取失败", delta="")
            else:
                delta_str = f"{change:+.2f} ({change_pct:+.2f}%)"
                st.metric(
                    label=name,
                    value=f"${price:,.2f}",
                    delta=delta_str,
                    delta_color="normal" if change >= 0 else "inverse",
                )


def display_kline(symbol: str, symbol_name: str):
    """展示K线图"""
    st.subheader(f"{symbol_name} K线走势")

    # K线周期选择
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        period = st.selectbox(
            "K线周期",
            options=list(KLINE_PERIODS.keys()),
            index=0,
            key=f"kline_period_{symbol}",
        )
    with col2:
        show_ma = st.checkbox("显示均线", value=True, key=f"show_ma_{symbol}")
        show_vol = st.checkbox("显示成交量", value=True, key=f"show_vol_{symbol}")

    # 获取数据
    df = get_kline_data(symbol, period)

    if df.empty:
        st.warning(f"暂无 {symbol_name} 的{period}数据")
        return

    # 绘制K线图
    fig = create_kline_chart(
        df,
        title=f"{symbol_name} ({symbol}) - {period}",
        show_ma=show_ma,
        show_volume=show_vol,
    )
    st.plotly_chart(fig, use_container_width=True)

    # 最新数据摘要
    with st.expander("📋 最新数据详情"):
        latest = df.iloc[-1]
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("开盘", f"${latest['open']:,.2f}")
        col2.metric("最高", f"${latest['high']:,.2f}")
        col3.metric("最低", f"${latest['low']:,.2f}")
        col4.metric("收盘", f"${latest['close']:,.2f}")
        col5.metric("成交量", f"{latest['volume']:,.0f}")


def add_custom_symbol():
    """添加自定义期货品种"""
    st.subheader("➕ 添加自定义期货品种")

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        new_name = st.text_input("品种名称", placeholder="如：原油", key="new_symbol_name")
    with col2:
        new_code = st.text_input("品种代码", placeholder="如：CL=F", key="new_symbol_code")
    with col3:
        st.write("")  # 占位
        st.write("")
        add_btn = st.button("添加", type="primary", use_container_width=True)

    # 快捷选择
    st.caption("💡 常用期货代码参考：")
    quick_cols = st.columns(4)
    quick_items = list(FUTURES_SYMBOLS.items())
    for i, (name, code) in enumerate(quick_items):
        with quick_cols[i % 4]:
            if st.button(f"{name} ({code})", key=f"quick_{code}"):
                st.session_state.new_symbol_name = name
                st.session_state.new_symbol_code = code
                st.rerun()

    if add_btn:
        if new_name and new_code:
            # 验证代码
            test_price = get_realtime_price(new_code)
            if test_price.get("price", 0) > 0:
                st.session_state.custom_symbols[new_name] = new_code
                st.success(f"✅ 已添加 {new_name} ({new_code})")
                st.rerun()
            else:
                st.error(f"❌ 无法获取 {new_code} 的数据，请检查代码是否正确")
        else:
            st.warning("请输入品种名称和代码")


def display_custom_symbols():
    """展示自定义期货品种"""
    if not st.session_state.custom_symbols:
        st.info("暂未添加自定义品种，请在上方添加")
        return

    # 实时报价
    custom_prices = get_custom_futures_prices(st.session_state.custom_symbols)
    display_price_cards(custom_prices, "📈 自定义期货品种实时报价")

    # 品种管理
    with st.expander("⚙️ 管理自定义品种"):
        for name, code in list(st.session_state.custom_symbols.items()):
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.text(name)
            with col2:
                st.code(code)
            with col3:
                if st.button("🗑️ 删除", key=f"del_{name}"):
                    del st.session_state.custom_symbols[name]
                    st.rerun()

    # K线图选择
    st.subheader("📈 自定义品种K线")
    selected_custom = st.selectbox(
        "选择品种",
        options=list(st.session_state.custom_symbols.keys()),
        format_func=lambda x: f"{x} ({st.session_state.custom_symbols[x]})",
        key="custom_symbol_select",
    )
    if selected_custom:
        display_kline(st.session_state.custom_symbols[selected_custom], selected_custom)


def main():
    init_session_state()

    # 页面标题
    st.title("📊 行情总览")
    st.markdown("---")

    # 1. 贵金属实时报价
    st.subheader("🥇 贵金属实时报价")
    default_prices = get_all_default_prices()
    display_price_cards(default_prices, "")

    # 自动刷新提示
    st.caption("💡 报价数据约有15分钟延迟，每5分钟自动刷新")

    st.markdown("---")

    # 2. 贵金属K线图
    st.subheader("📈 贵金属K线走势")
    selected_default = st.selectbox(
        "选择品种",
        options=list(DEFAULT_SYMBOLS.keys()),
        format_func=lambda x: f"{x} ({DEFAULT_SYMBOLS[x]})",
        key="default_symbol_select",
    )
    if selected_default:
        display_kline(DEFAULT_SYMBOLS[selected_default], selected_default)

    st.markdown("---")

    # 3. 自定义期货品种
    add_custom_symbol()
    st.markdown("---")
    display_custom_symbols()


main()
