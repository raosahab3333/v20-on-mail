#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import smtplib
from email.message import EmailMessage

THRESHOLD_PERCENT = 20
OUTPUT_CSV = True
EMAIL_ADDRESS = "vy807924@gmail.com"
EMAIL_PASSWORD = "owlaaaxtubkssdkj"
TO_EMAILS = [
    "vy807924@gmail.com",
    "thebigbull2410@gmail.com",
    "onlyprivate46@gmail.com"
]
CSV_NAME  = f"v20_signals_{datetime.now().strftime('%Y%m%d')}.csv"
HTML_NAME = f"v20_signals_{datetime.now().strftime('%Y%m%d')}.html"
START_DATE = (datetime.now() - timedelta(days=3 * 365)).strftime('%Y-%m-%d')
END_DATE   = datetime.now().strftime('%Y-%m-%d')

all_stocks = ['3MINDIA', 'AHLUCONT', 'AIAENG', 'AJANTPHARM', 'AKZOINDIA', 'ALKEM', 'ANANDRATHI', 'ANGELONE', 'APARINDS', 'APOLLOHOSP', 'ARCHEM', 'ASIANPAINT', 'ASTRAL', 'ASTRAZEN', 'AWL', 'AVANTIFEED', 'BAJAJ-AUTO', 'BAJAJHLDNG', 'BASF', 'BAYERCROP', 'BEL', 'BERGEPAINT', 'BIKAJI', 'BLUESTARCO', 'BOSCHLTD', 'BSOFT', 'BSE', 'CAPLIPOINT', 'CARBORUNIV', 'CAMS', 'CASTROLIND', 'CELLO', 'CERA', 'CHAMBLFERT', 'CDSL', 'CIPLA', 'CMSINFO', 'COALINDIA', 'COCHINSHIP', 'COLPAL', 'CONCORDBIO', 'COROMANDEL', 'CROMPTON', 'CRISIL', 'CUMMINSIND', 'DABUR', 'DBCORP', 'DEEPAKNTR', 'DHANUKA', 'DIXON', 'DMART', 'DRREDDY', 'ECLERX', 'EICHERMOT', 'EIDPARRY', 'EIHOTEL', 'ELECON', 'EMAMILTD', 'ENGINERSIN', 'ERIS', 'FINEORG', 'FORCEMOT', 'FORTIS', 'GANESHHOUC', 'GARFIBRES', 'GHCL', 'GILLETTE', 'GLAXO', 'GODFRYPHLP', 'GODREJCP', 'GODREJIND', 'GRINDWELL', 'GRSE', 'GSPL', 'GUJGASLTD', 'HAL', 'HAPPYFORGE', 'HAVELLS', 'HCLTECH', 'HEROMOTOCO', 'HINDUNILVR', 'HONAUT', 'ICICIGI', 'IEX', 'IGL', 'IMFA', 'INDHOTEL', 'INDIAMART', 'INFY', 'INGERRAND', 'INTELLECT', 'IONEXCHANG', 'IRCTC', 'ITC', 'JBCHEPHARM', 'JAIBALAJI', 'JIOFIN', 'JWL', 'JYOTHYLAB', 'JYOTICNC', 'KAJARIACER', 'KAMS', 'KFINTECH', 'KEI', 'KIRLOSBROS', 'KPIGREEN', 'KPITTECH', 'KPRMILL', 'KSCL', 'LALPATHLAB', 'LICI', 'LTIM', 'LTTS', 'MAHAPEXLTD', 'MAHSEAMLES', 'MANKIND', 'MANINFRA', 'MARICO', 'MARUTI', 'MCX', 'MCDHOLDING', 'MEDANTA', 'MGL', 'MISHTANN', 'MPHASIS', 'MRF', 'MSUMI', 'NAM-INDIA', 'NATCOPHARM', 'NBCC', 'NEULANDLAB', 'NEWGEN', 'NESCO', 'NIITLTD', 'NMDC', 'OFSS', 'PAGEIND', 'PETRONET', 'PFIZER', 'PGHH', 'PGHL', 'PIDILITIND', 'POLYCAB', 'POLYMED', 'QUESS', 'RADICO', 'RAILTEL', 'RATNAMANI', 'RELAXO', 'RITES', 'ROUTE', 'SANOFI', 'SCHAEFFLER', 'SEQUENT', 'SHARDAMOTR', 'SHAREINDIA', 'SHRIPISTON', 'SIEMENS', 'SKFINDIA', 'STYRENIX', 'SUMICHEM', 'SUNTV', 'SUPREMEIND', 'SURYAROSNI', 'TANLA', 'TATAELXSI', 'TATAMOTORS', 'TATATECH', 'TBOTEK', 'TEAMLEASE', 'TECHM', 'TIINDIA', 'TIMKEN', 'TITAGARH', 'TRITURBINE', 'UBL', 'ULTRACEMCO', 'UNITDSPR', 'UPL', 'URJAGLO', 'USHAMART', 'UTIAMC', 'VBL', 'VESUVIUS', 'VOLTAMP', 'VSTIND', 'WSTCSTPAPR', 'ZENSARTECH', 'ZFCVINDIA', 'ZENTEC', 'ADANIPORTS', 'JSWINFRA', 'ACC', 'M&M']

def download_data(symbol: str):
    try:
        df = yf.Ticker(symbol + ".NS").history(start=START_DATE, end=END_DATE)
        if df.empty:
            return None
        df = df[['Open', 'High', 'Low', 'Close']].dropna()
        df['MA200'] = df['Close'].rolling(window=200).mean()
        return df
    except Exception:
        return None

def find_v20_signals(df):
    signals = []
    latest_close = df['Close'].iloc[-1]
    streak_low = streak_high = None
    for idx in range(1, len(df)):
        cur = df.iloc[idx]
        if cur['Close'] > cur['Open']:
            streak_low  = cur['Low']  if streak_low  is None else min(streak_low,  cur['Low'])
            streak_high = cur['High'] if streak_high is None else max(streak_high, cur['High'])
            continue
        if streak_low and streak_high:
            pct_move = (streak_high - streak_low) / streak_low * 100
            if pct_move >= THRESHOLD_PERCENT and streak_low < cur.get('MA200', float('inf')):
                proximity = (latest_close - streak_low) / streak_low * 100
                signals.append((
                    df.index[idx].date(), round(streak_low, 2),
                    round(streak_high, 2), round(pct_move, 2),
                    round(latest_close, 2), round(proximity, 2)
                ))
        streak_low = streak_high = None
    return signals

def save_html(df, filename):
    table_html = df.to_html(classes="display nowrap", index=False).replace('<table ', '<table id="v20" ')
    html_out = """<!DOCTYPE html>
<html>
<head>
  <meta charset='utf-8'>
  <title>V20 Signals</title>
  <link rel='stylesheet' href='https://cdn.datatables.net/1.13.8/css/jquery.dataTables.min.css'>
  <style>
      body{{font-family:sans-serif;margin:20px}}
      table.dataTable{{width:100%!important}}
  </style>
</head>
<body>
  <h2>V20 Signals – {{date}}</h2>
  {{table}}
  <script src='https://code.jquery.com/jquery-3.7.1.min.js'></script>
  <script src='https://cdn.datatables.net/1.13.8/js/jquery.dataTables.min.js'></script>
  <script>
    $(document).ready(function(){{
      $('#v20').DataTable({{pageLength:25, order:[[6,'asc']]}});
      $('#v20 tbody tr').each(function(){{
          var prox = parseFloat($(this).find('td:eq(6)').text());
          if (prox < 0)          $(this).css('background','#f8d7da');
          else if (prox <= 5)    $(this).css('background','#d4edda');
      }});
    }});
  </script>
</body>
</html>""".replace("{date}", str(datetime.now().date())).replace("{table}", table_html)
    Path(filename).write_text(html_out, encoding='utf-8')
    print(f"✅ HTML saved → {filename}")

def send_email_with_html(html_file, to_email):
    msg = EmailMessage()
    msg['Subject'] = f'V20 Signals – {datetime.now().date()}'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email

    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    msg.set_content("Please view this email in an HTML-compatible client.")
    msg.add_alternative(html_content, subtype='html')

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            print(f"📧 Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

def main():
    signals = []
    for sym in all_stocks:
        df = download_data(sym)
        if df is None:
            continue
        for sig in find_v20_signals(df):
            sig_date, buy, sell, pct, close, prox = sig
            signals.append({
                'SignalDate': sig_date, 'Symbol': sym,
                'BuyAt': buy, 'SellAt': sell, '%Move': pct,
                'Close': close, 'Proximity%': prox
            })

    if not signals:
        print("No signals found.")
        return

    df_out = pd.DataFrame(signals)
    df_out.sort_values(by='Proximity%', ascending=True, inplace=True)
    save_html(df_out, HTML_NAME)

    if OUTPUT_CSV:
        df_out.to_csv(CSV_NAME, index=False)
        print(f"✅ CSV saved → {CSV_NAME}")

    for addr in TO_EMAILS:
        send_email_with_html(HTML_NAME, addr)

if __name__ == "__main__":
    main()
