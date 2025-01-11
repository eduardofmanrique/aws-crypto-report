import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
from io import BytesIO
import base64
from jinja2 import Environment, FileSystemLoader

from mb_api.auth import MbAuthenticator
from mb_api.resources.account import Account
from mb_api.resources.public_data import PublicData


class CryptoReport:
    def __init__(self, mb_auth: MbAuthenticator):
        self.__mb_auth = mb_auth

    def get_data(self) -> pd.DataFrame:
        account_resource = Account(self.__mb_auth)
        account = account_resource.list_accounts()[0]['id']
        balance = account_resource.list_balances(account)
        df = (
            pd
            .DataFrame(balance)
            .assign(symbol=lambda x: x['symbol']+'-BRL',
                    total=lambda x: x['total'].astype(float)
                    )
            .query('total>0')
        )
        public_data_resource = PublicData(self.__mb_auth)
        tickers = list(df['symbol'])
        tickers_price = public_data_resource.list_tickers(symbols=tickers)
        df = (
            df
            .merge(right=pd.DataFrame(tickers_price),
                   how='left',
                   left_on='symbol',
                   right_on='pair')
        )

        dfs_candle = []
        for ticker in tickers:
            tickers_candle = public_data_resource.list_candles(symbol=ticker,
                                                               resolution='1h',
                                                               to_timestamp=9999999999,
                                                               countback=75)
            df_tickers_candle = pd.DataFrame(tickers_candle)
            df_tickers_candle['symbol'] = ticker
            dfs_candle.append(df_tickers_candle)
        df_candle = pd.concat(dfs_candle)
        df = df_candle.merge(right=df,
                             how='left',
                             on='symbol')
        return df

    def transform_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df = (
            df
            .apply(pd.to_numeric, errors='ignore')
            .assign(t=lambda x: pd.to_datetime(x['t'], unit='s'),
                    variation=lambda x: (x['last']/x['open'])-1,
                    value=lambda x: x['last']*x['total'],
                    mktvalue=lambda x: x['vol']*x['last'])
        )
        return df.sort_values(by='mktvalue', ascending=False)

    def gen_pdf(self, df: pd.DataFrame):
        data = []
        for crypto in list(df['symbol'].unique()):
            df_crypto = df[df['symbol'] == crypto]
            df_crypto = df_crypto.sort_values('t')
            # Create the figure and axis
            fig, ax = plt.subplots(figsize=(10, 6))

            # Convert the dates to numeric format (matplotlib expects this)
            df_crypto['t'] = mdates.date2num(df_crypto['t'])

            # Plot candlesticks
            for i in range(len(df_crypto)):
                row = df_crypto.iloc[i]
                color = 'green' if row['c'] > row['o'] else 'red'

                # Plot the candlestick body
                ax.plot([row['t'], row['t']], [row['l'], row['h']], color='black')  # High to Low line
                ax.plot([row['t'], row['t']], [row['o'], row['c']], color=color, lw=6)  # Open to Close line

            # Format x-axis as dates
            ax.xaxis.set_major_locator(mdates.DayLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_minor_locator(mdates.HourLocator(interval=6))
            plt.xticks(rotation=45)

            # Title and labels
            ax.set_title("Candlestick Chart")
            ax.set_xlabel("Date")
            ax.set_ylabel("Price")

            # Improve layout and show grid
            ax.grid(True)
            fig.tight_layout()

            # Save the chart to a BytesIO buffer
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png', bbox_inches='tight')
            img_buffer.seek(0)

            # Encode the chart in base64
            chart_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')

            # Close the plt figure to free up memory
            plt.close(fig)

            data.append({
                "symbol": crypto,
                "value": df_crypto['value'].iloc[0],
                "variation": df_crypto['variation'].iloc[0],
                "vol": df_crypto['vol'].iloc[0],
                "last": df_crypto['last'].iloc[0],
                "chart_image": chart_base64
            })

        env = Environment(loader=FileSystemLoader("report"))
        template = env.get_template("template.html")

        html_content = template.render(data=data, percent="%")
        print(html_content)
        with open('crypto_report.html', "w", encoding="utf-8") as f:
            f.write(html_content)

    def gen_text(self, df: pd.DataFrame):
        pass

    def gen_report(self):
        df = self.get_data()
        df = self.transform_data(df)
        self.gen_pdf(df)

