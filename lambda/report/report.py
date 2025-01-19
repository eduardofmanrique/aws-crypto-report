import pandas as pd
from fpdf import FPDF
import base64
import io

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
            .assign(symbol=lambda x: x['symbol'] + '-BRL',
                    total=lambda x: x['total'].astype(float))
            .query('total > 0 or symbol in ["BTC-BRL", "ETH-BRL"]')
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

        return df

    def transform_data(self, df: pd.DataFrame) -> pd.DataFrame:
        # Perform transformations and formatting in one step
        df = (
            df
            .apply(pd.to_numeric, errors='ignore')
            .assign(
                variation=lambda x: ((x['last'] / x['open']) - 1).apply(lambda y: f"{y:.2%}".replace(".", ",")),
                value=lambda x: (x['last'] * x['total']),
                mktvalue=lambda x: (x['vol'] * x['last']),
                vol=lambda x: x['vol'].apply(
                    lambda y: f"{y:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")),
                last=lambda x: x['last'].apply(
                    lambda y: f"{y:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")),
            )
            .sort_values(by='mktvalue', ascending=False)
        )
        return df

    def gen_pdf(self, df: pd.DataFrame):

        df = (df
              .copy()
              .sort_values('value', ascending=False)
              .assign(value= lambda x: x['value'].apply(lambda y: f"{y:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))))

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.set_font("Arial", style="B", size=14)
        pdf.cell(0, 10, txt="Cryptocurrency Report", ln=True, align="C")
        pdf.ln(10)

        col_widths = [30, 40, 40, 40, 40]
        headers = ["Symbol", "Value", "Variation", "Volume", "Last"]
        table_width = sum(col_widths)
        margin = (210 - table_width) / 2

        pdf.set_fill_color(200, 200, 200)
        pdf.set_font("Arial", style="B", size=12)
        pdf.set_x(margin)  # Center table
        for header, width in zip(headers, col_widths):
            pdf.cell(width, 10, txt=header, border=1, align="C", fill=True)
        pdf.ln()

        pdf.set_font("Arial", size=10)
        fill = False  # Toggle fill color
        for _, row in df.iterrows():
            pdf.set_x(margin)  # Center table
            pdf.set_fill_color(240, 240, 240)  # Light gray for alternating rows
            pdf.cell(col_widths[0], 10, txt=row['symbol'], border=1, align="C", fill=fill)
            pdf.cell(col_widths[1], 10, txt=row['value'], border=1, align="C", fill=fill)
            pdf.cell(col_widths[2], 10, txt=row['variation'], border=1, align="C", fill=fill)
            pdf.cell(col_widths[3], 10, txt=row['vol'], border=1, align="C", fill=fill)
            pdf.cell(col_widths[4], 10, txt=row['last'], border=1, align="C", fill=fill)
            pdf.ln()
            fill = not fill

        pdf_buffer = io.BytesIO()
        pdf.output(pdf_buffer)
        pdf_buffer.seek(0)

        base64_pdf = base64.b64encode(pdf_buffer.read()).decode('utf-8')
        return base64_pdf

    def gen_text(self, df: pd.DataFrame):
        data = (df[['symbol', 'last', 'variation']]
                .drop_duplicates()
                .to_dict(orient='records'))
        return "\n\n".join([f"{item['symbol']} | R$ {item['last']} | {item['variation']}" for item in data])

    def gen_report(self):
        df = self.get_data()
        df = self.transform_data(df)
        return {
            'pdf': self.gen_pdf(df),
            'text': self.gen_text(df)
        }

