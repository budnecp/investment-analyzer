"""
💰 资金面分析页面（占位）
后续实现：持仓量分析、资金流向、多空比例
"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DEFAULT_SYMBOLS

st.set_page_config(
    page_title="资金面",
    page_icon="💰",
    layout="wide",
)


def main():
    st.title("💰 资金面分析")
    st.markdown("---")

    st.info("🚧 资金面分析模块正在建设中...")

    st.markdown("""
    ### 规划功能

    #### 📊 持仓量分析
    - 主力合约持仓量变化
    - 持仓量与价格的关系
    - 持仓量异动监控

    #### 💸 资金流向
    - 主力资金流入流出
    - 大单/中单/小单资金流向
    - 资金净流入排名

    #### ⚖️ 多空比例
    - 多空持仓比例
    - 多空力量对比图
    - 主力多空变化趋势

    ---

    > 📌 数据来源规划：交易所持仓数据、CFTC持仓报告
    """)

    # 品种选择占位
    st.subheader("选择品种")
    selected = st.selectbox(
        "品种",
        options=list(DEFAULT_SYMBOLS.keys()),
        disabled=True,
    )

    st.caption("该功能需要接入交易所持仓数据API，正在规划中")


main()
