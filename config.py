"""
投资分析工具 - 配置文件
"""
import os

# ==================== 应用配置 ====================
APP_TITLE = "投资分析工具"
APP_ICON = "📊"
LAYOUT = "wide"

# ==================== 数据源配置 ====================
# yfinance 品种代码映射
DEFAULT_SYMBOLS = {
    "黄金": "GC=F",
    "白银": "SI=F",
    "铂金": "PL=F",
}

# 期货品种代码映射（可扩展）
FUTURES_SYMBOLS = {
    "原油": "CL=F",
    "天然气": "NG=F",
    "铜": "HG=F",
    "大豆": "ZS=F",
    "小麦": "ZW=F",
    "玉米": "ZC=F",
    "糖": "SB=F",
    "棉花": "CT=F",
}

# K线周期映射
KLINE_PERIODS = {
    "日K": "1d",
    "周K": "1wk",
    "月K": "1mo",
}

# 数据获取天数
DATA_DAYS = {
    "日K": 365,
    "周K": 730,
    "月K": 1825,
}

# ==================== 技术指标默认参数 ====================
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

KDJ_PERIOD = 9
KDJ_SMOOTH_K = 3
KDJ_SMOOTH_D = 3

RSI_PERIOD = 14

MA_PERIODS = [5, 10, 20, 60, 120, 250]

# ==================== 缠论参数 ====================
CHAN_MIN_BARS = 4  # 最少包含K线数
CHAN_TOLERANCE = 0.0  # 价格容忍度

# ==================== 波浪理论参数 ====================
WAVE_MIN_SIZE = 0.03  # 最小波浪幅度比例

# ==================== 博主/消息源配置 ====================
BLOGGER_SOURCES = {
    "当铺财经": {"platform": "抖音", "url": ""},
    "内蒙古小顽童": {"platform": "抖音", "url": ""},
    "百年财经": {"platform": "抖音", "url": ""},
    "王总黄金": {"platform": "抖音", "url": ""},
    "AG Thorson": {"platform": "Gold-Eagle", "url": "https://www.gold-eagle.com/"},
}

# 新闻API（预留）
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "")

# ==================== 页面配置 ====================
PAGE_CONFIG = {
    "page_title": APP_TITLE,
    "page_icon": APP_ICON,
    "layout": LAYOUT,
    "initial_sidebar_state": "expanded",
}
