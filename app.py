import pandas as pd
import yfinance as yf
import altair as alt
import streamlit as st

st.title("米国株価可視化アプリ")

st.sidebar.write('''
# GAFA株価
こちらは株価可視化ツールです。いかのオプションから表示日数を指定
''')

st.sidebar.write('''
## 表示日数選択
''')
days = st.sidebar.slider("日数", 1, 200, 30)


st.write(f'''
過去**{days}日間**のGAFA株価
''')

@st.cache
def get_data(tickers, days):

    df = pd.DataFrame()

    for company in tickers.keys():

        tkr = yf.Ticker(tickers[company])

        hist = tkr.history(period = f"{days}d")

        hist.index = hist.index.strftime("%d %B %Y")

        hist = hist[["Close"]]
        hist.rename(columns = {"Close" : tickers[company]}, inplace = True)

        hist = hist.T
        hist.index.name = "Ticker"
        df = pd.concat([df, hist], axis = 0)

    return df

try:
    st.sidebar.write('''
    ## 株価の範囲指定
    ''')
    ymin, ymax = st.sidebar.slider("範囲を指定してください", 0.0, 4000.0, (0.0, 4000.0))


    tickers = {
        "apple" : "AAPL",
        "meta" : "FB",
        "alphabet" : "GOOGL",
        "amazon" : "AMZN",
        "tesla" : "TSLA"
    }

    df = get_data(tickers, days)


    companies = st.multiselect(
        "銘柄を選択してください。",
        list(df.index),
        ["GOOGL","AAPL", "FB", "AMZN" ]
    )

    if not companies:
        st.error("少なくとも1銘柄は選んでください。")
    else:
        data = df.loc[companies]
        st.write("### 株価（USD）", data.sort_index())
        data = data.T.reset_index()
        data = pd.melt(data, id_vars = ["Date"]).rename(columns = {"value" : "Stock Prices(USD)"})
        chart = (
            alt.Chart(data)
            .mark_line(opacity = 0.8, clip = True)
            .encode(x = "Date:T",
                    y = alt.Y("Stock Prices(USD):Q", stack = None, scale = alt.Scale(domain = [ymin, ymax])),
                    color = "Ticker:N"
            ) 
        )
    st.altair_chart(chart, use_container_width = True)
except:
    st.error(
        "エラーが起きています。"
    )