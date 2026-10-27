import time
import random
import pandas as pd
import requests
from sqlalchemy import create_engine, text
import concurrent.futures
import json

import os
db_url = os.environ.get('DB_URL', 'postgresql://comovie:comovie@localhost:5432/toko-dwinika')


# Create the SQLAlchemy engine
engine = create_engine(db_url)

def ensure_schema():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS jwt_tokens (
                id SERIAL PRIMARY KEY,
                token TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))
        conn.commit()
    print("[schema] jwt_tokens table ensured.")

def sanitize_dataframe(df):
    """
    Mengubah kolom yang berisi dict atau list menjadi string JSON
    agar aman dimasukkan ke PostgreSQL.
    """
    df_clean = df.copy()
    for col in df_clean.columns:
        # Cek jika ada elemen dalam kolom bertipe dict atau list
        df_clean[col] = df_clean[col].apply(
            lambda x: json.dumps(x) if isinstance(x, (dict, list)) else x
        )
    return df_clean

def safe_to_sql(df, table_name):
    # 1. Bersihkan dataframe (konversi dict/list ke JSON string)
    df = sanitize_dataframe(df)

    from sqlalchemy import inspect
    insp = inspect(engine)
    if insp.has_table(table_name):
        existing_cols = {col['name'] for col in insp.get_columns(table_name)}
        for col in df.columns:
            if col not in existing_cols:
                dtype = df[col].dtype
                if pd.api.types.is_integer_dtype(dtype):
                    sql_type = "BIGINT"
                elif pd.api.types.is_float_dtype(dtype):
                    sql_type = "DOUBLE PRECISION"
                elif pd.api.types.is_bool_dtype(dtype):
                    sql_type = "BOOLEAN"
                elif pd.api.types.is_datetime64_any_dtype(dtype):
                    sql_type = "TIMESTAMP"
                else:
                    sql_type = "TEXT"
                try:
                    with engine.connect() as conn:
                        conn.execute(text(
                            f'ALTER TABLE "{table_name}" ADD COLUMN "{col}" {sql_type}'
                        ))
                        conn.commit()
                    print(f"[schema] Added column '{col}' ({sql_type}) to '{table_name}'")
                except Exception:
                    pass
    try:
        df.to_sql(table_name, engine, if_exists='append', index=False, method="multi")
    except Exception as e:
        msg = str(e).split('\n')[0][:300]
        print(f"[ERROR] to_sql '{table_name}': {msg}")
        raise

jwt = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjI3YWExYmM2MzBiZjBhZDIzMmM3YmEwMTc1MGM5M2NiMmMyODNlMzgyODRkZTQzYzNjYzMwYWEyZTUwMDQ1MjY1YzY4N2E3MWYyMTMzNzNlIn0.eyJhdWQiOiIyIiwianRpIjoiMjdhYTFiYzYzMGJmMGFkMjMyYzdiYTAxNzUwYzkzY2IyYzI4M2UzODI4NGRlNDNjM2NjMzBhYTJlNTAwNDUyNjVjNjg3YTcxZjIxMzM3M2UiLCJpYXQiOjE3NTQ5NzE1NTQsIm5iZiI6MTc1NDk3MTU1NCwiZXhwIjoxNzU3NTYzNTU0LCJzdWIiOiI2MjQyNjIiLCJzY29wZXMiOltdfQ.lzoLem4sBhPiw5Un7-ZOiCKNOzfsHwEfXQ2iP6IBFBaYLhTsEKjeS_yhWGymJe3yD5ORPOLk63NiZ2H3XPwT1cyp3M1HoPdyczEyOlsCp3PI0Eykog4bwbRFra9fmv59irHYjmo0eIAVRSqAWgPI7-GWR2mFrwZ-dVhkngQ_lsSphQ6Kl_ppQgKEg5G6YJPYneYg1DtFLL5MSQ4x6XfpnRKwqAWp2UcrUPoxvFSeoACvjL1tJroTigg4X8Pr-GNNmSejSLlkjaneEkbLIdwYAcIRH9qTbfOHlItWne1vvpzO5R3f8mmYpew89fOhhr14r7qju-UEELkX6_wevzxPAIht_cygJVMb4dww7DbzTt6ueL4jXaTKMVAPVDQrfH3BTE0yYSwAM6EklMRx46548aCD4BykcbPdZB3yDe3E6fuO38q8jbdqzlJoJCs5Cp3qpv9RcbkubmrlJpFjVdD08MYhyp-XYAMFUBj48dl4JZG5NGUvL9bV3vYpfuXfEJ0hZ3WTk24LQfAJEDaxeoSf_6TJyk7xKFFbHcQSRzkT4QCrJUIkgs_8KKAwqKmi-vGhrX56zhJLbtXQXKfd83jKTmmEiuUDI4GiUvJAUepkvT88Tj4YfAmZhqCYMCqjd6MJ7hVxJRON5XzV0_MeCCxceKV30cAZzbjwgm8qeFgjXiA"

def hello():
    print("Hello World")


def login():
#    url = 'https://api-dash.olsera.co.id/api/tokodwinika/admin/v1/id/login'

    url = 'https://api-dash.olsera.co.id/oauth/token'
    payload = {
        "client_id": 2,
        "client_secret": "0XqbhEW6E72GNHn0iIM7Ui1GgB8jny91wYnXAIb8",
        "grant_type": "password",
        "username": "dwinika_dim@yahoo.com",
        "password": "dwinika123!"
    }
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/json',
        'origin': 'https://dashboard.olsera.co.id',
        'referer': 'https://dashboard.olsera.co.id/',
        'sec-ch-ua': '"Not/A)Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    }

    response = requests.request("POST", url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        jwt = data['access_token']
        # Save the JWT to the database
        with engine.connect() as connection:
            connection.execute(text("INSERT INTO jwt_tokens (token) VALUES (:token)"), {"token": jwt})
        return jwt
    else:
        print(response.text)
        return None


#def login():
#    url = 'https://api-dash.olsera.co.id/api/tokodwinika/admin/v1/id/login'

#    url = 'https://api-dash.olsera.co.id/oauth/token'
#    payload = {
#        "client_id": 2,
#        "client_secret": "0XqbhEW6E72GNHn0iIM7Ui1GgB8jny91wYnXAIb8",
#        "grant_type": "password",
#        "username": "dwinika_dim@yahoo.com",
#        "password": "dwinika123!"
#    }
#    headers = {
#        'accept': 'application/json, text/plain, */*',
#        'accept-language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
#        'content-type': 'application/json',
#        'origin': 'https://dashboard.olsera.co.id',
#        'referer': 'https://dashboard.olsera.co.id/',
#        'sec-ch-ua': '"Not/A)Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
#        'sec-ch-ua-mobile': '?0',
#        'sec-ch-ua-platform': '"Linux"',
#        'sec-fetch-dest': 'empty',
#        'sec-fetch-mode': 'cors',
#        'sec-fetch-site': 'same-site',
#        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
#    }

#    response = requests.request("POST", url, headers=headers, json=payload)
#    if response.status_code == 200:
#        data = response.json()
#        jwt = data['access_token']
#        # Save the JWT to the database
#        with engine.connect() as connection:
#            connection.execute("INSERT INTO jwt_tokens (token) VALUES (%s)", (jwt,))
#        return jwt
#    else:
#        print(response.text)
#        return None

#def fetch_data_from_api(url, token=None, payload=None):
#    if token == None
#       token = login()
#
#    headers = {
#        'authorization': f'Bearer {token}',
#        'accept': 'application/json, text/plain, */*',
#        'accept-language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
#        'origin': 'https://dashboard.olsera.co.id',
#        'priority': 'u=1, i',
#        'referer': 'https://dashboard.olsera.co.id/',
#        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
#        'sec-ch-ua-mobile': '?0',
#        'sec-ch-ua-platform': '"Linux"',
#        'sec-fetch-dest': 'empty',
#        'sec-fetch-mode': 'cors',
#        'sec-fetch-site': 'same-site',
#        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
#    }
#
#    response = requests.request("GET", url, headers=headers, params=payload)
#
#    if response.status_code == 200:
#        data = response.json()
#        df = pd.json_normalize(data['data'])
#        print(df)
#        meta = data.get('meta', None)
#        return df, meta
#    else:
#        return None, None


import threading
_throttle_lock = threading.Lock()
_next_slot = 0.0
MIN_INTERVAL = float(os.environ.get('API_MIN_INTERVAL', '1.5'))  # detik antar request (global, semua thread)
MAX_429_RETRY = 6


def _throttle():
    global _next_slot
    with _throttle_lock:
        now = time.monotonic()
        wait = max(0.0, _next_slot - now)
        _next_slot = max(now, _next_slot) + MIN_INTERVAL
    if wait:
        time.sleep(wait)


def _get_with_throttle(url, headers, payload):
    for attempt in range(MAX_429_RETRY + 1):
        _throttle()
        response = requests.request("GET", url, headers=headers, params=payload)
        if response.status_code != 429 or attempt == MAX_429_RETRY:
            return response
        try:
            delay = float(response.headers.get('Retry-After', ''))
        except ValueError:
            delay = min(2 ** attempt * 2, 60)  # 2,4,8,16,32,60
        delay += random.random()
        print(f"⏳ 429 Too Many Requests, retry {attempt + 1}/{MAX_429_RETRY} dalam {delay:.1f}s")
        global _next_slot
        with _throttle_lock:  # hentikan semua thread, bukan cuma yang kena 429
            _next_slot = max(_next_slot, time.monotonic() + delay)


def fetch_data_from_api(url, token=None, payload=None):
    print(url)
    # 1. Cek token dengan cara yang benar (PEP 8)
    if token is None:
        token = login()
        if token is None:
            print("Gagal mendapatkan token.")
            return None, None

    headers = {
        'authorization': f'Bearer {token}',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
        # 2. PERBAIKAN: Hapus spasi berlebih di akhir URL
        'origin': 'https://dashboard.olsera.co.id',
        'priority': 'u=1, i',
        'referer': 'https://dashboard.olsera.co.id/',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    }

    try:
        response = _get_with_throttle(url, headers, payload)

        # 3. Cek Status Code
        if response.status_code != 200:
            print(f"⚠️ Request gagal: Status {response.status_code}")
            return None, None

        # 4. Cek jika response kosong
        if not response.text.strip():
            print("⚠️ Response body kosong")
            return None, None

        # 5. AMAN: Parsing JSON dengan Try-Except
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            print(f"❌ Gagal parse JSON: {e}")
            print(f"🔍 Isi Response: {response.text[:300]}") # Debug: lihat isi response
            return None, None

        # 6. AMAN: Cek keberadaan key 'data' sebelum diakses
        if 'data' not in data:
            print(f"⚠️ Key 'data' tidak ditemukan. Keys tersedia: {list(data.keys())}")
            return None, None

        # 7. Proses data
        df = pd.json_normalize(data['data'])
        meta = data.get('meta', None)
        return df, meta

    except requests.exceptions.RequestException as e:
        print(f"❌ Network Error: {e}")
        return None, None

def get_data_barang():
    url = 'https://api-dash.olsera.co.id/api/tokodwinika/admin/v1/id/product'
    payload = { "per_page":100, "page": 1, "sort_column": "id", "sort_type": "desc" }
    jwt = login()
    df, meta = fetch_data_from_api(url, token=jwt, payload=payload)

    last_id = pd.DataFrame({'last_id': [0]})

    from sqlalchemy import inspect
    if inspect(engine).has_table('barang'):
        last_id = pd.read_sql_query("SELECT max(id) as last_id FROM barang", engine).fillna(0)

    total_pages = meta['last_page']
    rows_saved = 0
    print(f"[barang] Starting fetch: {total_pages} page(s) available")

    while meta['current_page'] <= meta['last_page']:
        current_page = meta['current_page']
        print(f"[barang] Page {current_page}/{total_pages} ...")
        df = df[df['id'] > last_id['last_id'][0]]

        if df.empty:
            print(f"[barang] No new rows on page {current_page}, stopping.")
            break

        if 'buy_price' in df.columns:
            df['buy_price'] = pd.to_numeric(df['buy_price'], errors='coerce')

        safe_to_sql(df, 'barang')
        rows_saved += len(df)
        print(f"[barang] Page {current_page}/{total_pages} ✅ saved {len(df)} rows (total saved: {rows_saved})")

        payload['page'] += 1
        df, meta = fetch_data_from_api(url, token=jwt, payload=payload)
        sleep_time = random.randint(2, 10)
        time.sleep(sleep_time)

    print(f"[barang] Done. Total rows saved: {rows_saved}")

def get_data_transaksi():
    url = 'https://api-dash.olsera.co.id/api/tokodwinika/admin/v1/id/transaction'
    payload = { "per_page":100, "page": 1, "sort_column": "id", "sort_type": "desc" }
    jwt = login()

    df, meta = fetch_data_from_api(url, token=jwt, payload=payload)
    last_id = pd.DataFrame({'last_id': [0]})

    from sqlalchemy import inspect
    if inspect(engine).has_table('transaksi'):
        last_id = pd.read_sql_query("SELECT max(id) as last_id FROM transaksi", engine)

    total_pages = meta['last_page']
    rows_saved = 0
    print(f"[transaksi] Starting fetch: {total_pages} page(s) available")

    while meta['current_page'] <= meta['last_page']:
        current_page = meta['current_page']
        print(f"[transaksi] Page {current_page}/{total_pages} ...")
        df = df[df['id'] > last_id['last_id'][0]]

        if df.empty:
            print(f"[transaksi] No new rows on page {current_page}, stopping.")
            break

        safe_to_sql(df, 'transaksi')
        rows_saved += len(df)
        print(f"[transaksi] Page {current_page}/{total_pages} ✅ saved {len(df)} rows (total saved: {rows_saved})")

        payload['page'] += 1
        df, meta = fetch_data_from_api(url, token=jwt, payload=payload)
        sleep_time = random.randint(2, 10)
        time.sleep(sleep_time)

    print(f"[transaksi] Done. Total rows saved: {rows_saved}")

def get_data_pelanggan():
    url = 'https://api-dash.olsera.co.id/api/tokodwinika/admin/v1/id/customer'
    payload = { "per_page":100, "page": 1, "sort_column": "id", "sort_type": "desc" }
    jwt = login()
    df, meta = fetch_data_from_api(url, token=jwt, payload=payload)
    # df['membership_vehicle'] = df['membership_vehicle'].astype(str)
    # df['update_log'] = df['update_log'].astype(str)

    from sqlalchemy import inspect
    if inspect(engine).has_table('customers'):
        last_id = pd.read_sql_query("SELECT max(id) as last_id FROM customers", engine)
        if last_id['last_id'][0] is None:
            last_id['last_id'][0] = 0
    else:
        last_id = pd.DataFrame({'last_id': [0]})

    total_pages = meta['last_page']
    rows_saved = 0
    print(f"[pelanggan] Starting fetch: {total_pages} page(s) available")

    while meta['current_page'] <= meta['last_page']:
        current_page = meta['current_page']
        print(f"[pelanggan] Page {current_page}/{total_pages} ...")
        try:
            df = df[df['id'] > last_id['last_id'][0]]

            if df.empty:
                print(f"[pelanggan] No new rows on page {current_page}, stopping.")
                break

            safe_to_sql(df, 'customers')
            rows_saved += len(df)
            print(f"[pelanggan] Page {current_page}/{total_pages} ✅ saved {len(df)} rows (total saved: {rows_saved})")

            payload['page'] += 1
            next_df, next_meta = None, None
            for attempt in range(3):
                next_df, next_meta = fetch_data_from_api(url, token=jwt, payload=payload)
                if next_df is not None:
                    break
                print(f"[pelanggan] Fetch page {payload['page']} failed (attempt {attempt + 1}/3), re-login & retry")
                time.sleep(5 * (attempt + 1))
                jwt = login()
            if next_df is None:
                print(f"[pelanggan] ❌ Giving up at page {payload['page']}")
                break
            df, meta = next_df, next_meta
            for col in ('membership_vehicle', 'update_log'):
                if col in df.columns:
                    df[col] = df[col].astype(str)
            sleep_time = random.randint(2, 5)
            time.sleep(sleep_time)
        except Exception as e:
            print(f"[pelanggan] ❌ Error on page {current_page}: {e}")
            break

    print(f"[pelanggan] Done. Total rows saved: {rows_saved}")

def get_data_penjualan():
    jwt = login()
    url = 'https://permissions-api-dash.olsera.co.id/api/tokodwinika/admin/v1/id/closeorder'
    payload = { "per_page":100, "page": 1, "sort_column": "id", "sort_type": "desc" }
    df, meta = fetch_data_from_api(url, token=jwt, payload=payload)
    for col in df.columns:
        if isinstance(df[col].iloc[0], dict):
            df[col] = df[col].astype(str)

    last_id = pd.DataFrame({'last_id': [0]})
    from sqlalchemy import inspect
    if inspect(engine).has_table('orders'):
        last_id = pd.read_sql_query("SELECT max(id) as last_id FROM orders", engine)

    if last_id.empty or last_id['last_id'][0] is None:
        last_id['last_id'][0] = 0

    total_pages = meta['last_page']
    rows_saved = 0
    print(f"[penjualan] Starting fetch: {total_pages} page(s) available")

    while meta['current_page'] <= meta['last_page']:
        current_page = meta['current_page']
        print(f"[penjualan] Page {current_page}/{total_pages} ...")
        df = df[df['id'] > last_id['last_id'][0]]

        if df.empty:
            print(f"[penjualan] No new rows on page {current_page}, stopping.")
            break

        safe_to_sql(df, 'orders')
        rows_saved += len(df)
        print(f"[penjualan] Page {current_page}/{total_pages} ✅ saved {len(df)} rows (total saved: {rows_saved})")

        payload['page'] += 1
        df, meta = fetch_data_from_api(url, token=jwt, payload=payload)
        sleep_time = random.randint(2, 5)
        time.sleep(sleep_time)

    print(f"[penjualan] Done. Total rows saved: {rows_saved}")

def get_data_penjualani_revision():
    jwt = login()
    url = 'https://permissions-api-dash.olsera.co.id/api/tokodwinika/admin/v1/id/closeorder'
    payload = {  "search": "57B226040600014256", "total": 7037, "crrentPage": 1, "per_page":100, "page": 1, "sort_column": "id", "sort_type": "desc" }
    df, meta = fetch_data_from_api(url, token=jwt, payload=payload)
    for col in df.columns:
        if isinstance(df[col].iloc[0], dict):
            df[col] = df[col].astype(str)

    last_id = pd.DataFrame({'last_id': [0]})
    from sqlalchemy import inspect
    if inspect(engine).has_table('orders'):
        last_id = pd.read_sql_query("SELECT max(id) as last_id FROM orders", engine)

    if last_id.empty or last_id['last_id'][0] is None:
        last_id['last_id'][0] = 0

    total_pages = meta['last_page']
    rows_saved = 0
    print(f"[penjualan] Starting fetch: {total_pages} page(s) available")

    while meta['current_page'] <= meta['last_page']:
        current_page = meta['current_page']
        print(f"[penjualan] Page {current_page}/{total_pages} ...")
    #    df = df[df['id'] > last_id['last_id'][0]]

        if df.empty:
            print(f"[penjualan] No new rows on page {current_page}, stopping.")
            break

        safe_to_sql(df, 'orders')
        rows_saved += len(df)
        print(f"[penjualan] Page {current_page}/{total_pages} ✅ saved {len(df)} rows (total saved: {rows_saved})")

        payload['page'] += 1
        df, meta = fetch_data_from_api(url, token=jwt, payload=payload)
        sleep_time = random.randint(2, 5)
        time.sleep(sleep_time)

    print(f"[penjualan] Done. Total rows saved: {rows_saved}")


def get_data_penjualan_detail():
    from sqlalchemy import inspect
    insp = inspect(engine)
    if not insp.has_table('orders'):
        print("[penjualan_detail] 'orders' table not found, nothing to process.")
        return
    if not insp.has_table('orders_detail'):
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE orders_detail (
                    id BIGINT,
                    sales_order_id BIGINT
                )
            """))
            conn.commit()
        print("[penjualan_detail] Created 'orders_detail' table.")
    import threading
    df_order = pd.read_sql_query("SELECT * FROM orders WHERE id not in(select sales_order_id from orders_detail)", engine)
    jwt = login()

    order_ids = df_order['id'].tolist()
    total = len(order_ids)
    print(f"[penjualan_detail] Total orders to process: {total}")

    if total == 0:
        print("[penjualan_detail] Nothing to process.")
        return

    counter = {"done": 0, "success": 0, "failed": 0}
    lock = threading.Lock()

    def process_row(order_id):
        try:
            url = f'https://permissions-api-dash.olsera.co.id/api/tokodwinika/admin/v1/id/closeorder/{order_id}'
            df, meta = fetch_data_from_api(url, token=jwt, payload=None)
            df_item = pd.json_normalize(df['orderitems'][0])

            safe_to_sql(df_item, 'orders_detail')
            sleep_time = random.randint(1, 2)
            time.sleep(sleep_time)

            with lock:
                counter["done"] += 1
                counter["success"] += 1
                print(f"[penjualan_detail] [{counter['done']}/{total}] ✅ order_id={order_id} saved ({counter['failed']} failed)")

        except Exception as e:
            with lock:
                counter["done"] += 1
                counter["failed"] += 1
                print(f"[penjualan_detail] [{counter['done']}/{total}] ❌ order_id={order_id} failed: {e}")

    # Process rows in parallel with 4 workers
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(process_row, order_ids)

    print(f"[penjualan_detail] Done. {counter['success']} succeeded, {counter['failed']} failed out of {total}.")

def get_data_pembelian():
    jwt = login()
    url = 'https://api-dash.olsera.co.id/api/tokodwinika/admin/v1/id/openpurchase'
    payload = { "per_page":100, "page": 1, "sort_column": "id", "sort_type": "desc" }
    df, meta = fetch_data_from_api(url, token=jwt, payload=payload)

    from sqlalchemy import inspect
    if inspect(engine).has_table('purchase'):
        last_id = pd.read_sql_query("SELECT max(id) as last_id FROM purchase", engine)
    else:
        last_id = pd.DataFrame({'last_id': [0]})

    total_pages = meta['last_page']
    rows_saved = 0
    print(f"[pembelian] Starting fetch: {total_pages} page(s) available")

    while meta['current_page'] <= meta['last_page']:
        current_page = meta['current_page']
        print(f"[pembelian] Page {current_page}/{total_pages} ...")
        df = df[df['id'] > last_id['last_id'][0]]

        if df.empty:
            print(f"[pembelian] No new rows on page {current_page}, stopping.")
            break

        safe_to_sql(df, 'purchase')
        rows_saved += len(df)
        print(f"[pembelian] Page {current_page}/{total_pages} ✅ saved {len(df)} rows (total saved: {rows_saved})")

        payload['page'] += 1
        df, meta = fetch_data_from_api(url, token=jwt, payload=payload)
        sleep_time = random.randint(2, 10)
        time.sleep(sleep_time)

    print(f"[pembelian] Done. Total rows saved: {rows_saved}")

def get_data_pembelian_detail():
    from sqlalchemy import inspect
    insp = inspect(engine)
    if not insp.has_table('purchase'):
        print("[pembelian_detail] 'purchase' table not found, nothing to process.")
        return
    if not insp.has_table('purchase_detail'):
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE purchase_detail (
                    id BIGINT,
                    purchase_order_id BIGINT
                )
            """))
            conn.commit()
        print("[pembelian_detail] Created 'purchase_detail' table.")
    import threading
    df_purchase = pd.read_sql_query("SELECT * FROM purchase WHERE id NOT IN (SELECT purchase_order_id FROM purchase_detail)", engine)
    jwt = login()

    purchase_ids = df_purchase['id'].tolist()
    total = len(purchase_ids)
    print(f"Total purchases to process: {total}")

    if total == 0:
        print("Nothing to process.")
        return

    counter = {"done": 0, "success": 0, "failed": 0}
    lock = threading.Lock()

    def process_row(purchase_id):
        try:
            url = f'https://api-dash.olsera.co.id/api/tokodwinika/admin/v1/id/openpurchase/{purchase_id}'
            df, meta = fetch_data_from_api(url, token=jwt, payload=None)
            df_item = pd.json_normalize(df['purchaseitems'][0])

            # Ensure you have a way to handle engine in a thread-safe manner
            safe_to_sql(df_item, 'purchase_detail')
            sleep_time = random.randint(1, 2)
            time.sleep(sleep_time)

            with lock:
                counter["done"] += 1
                counter["success"] += 1
                print(f"[{counter['done']}/{total}] ✅ purchase_id={purchase_id} saved ({counter['failed']} failed)")

        except Exception as e:
            with lock:
                counter["done"] += 1
                counter["failed"] += 1
                print(f"[{counter['done']}/{total}] ❌ purchase_id={purchase_id} failed: {e}")

    # Process rows in parallel with 4 workers
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(process_row, purchase_ids)

    print(f"\nDone. {counter['success']} succeeded, {counter['failed']} failed out of {total}.")

def get_data_pelanggan2():
    jwt = login()
    print(jwt)
#    url = 'https://api-dash.olsera.co.id/api/tokodwinika/admin/v1/id/customer'
#    payload = { "per_page":100, "page": 1, "sort_column": "id", "sort_type": "desc" }
#    df, meta = fetch_data_from_api(url, token=jwt, payload=payload)
#    df['membership_vehicle'] = df['membership_vehicle'].astype(str)
#    df['update_log'] = df['update_log'].astype(str)

    # select from database get last id
#    last_id = pd.read_sql_query("SELECT max(id) as last_id FROM customers", engine)
#    if last_id['last_id'][0] is None:
#        last_id['last_id'][0] = 0


 #   while meta['current_page'] <= meta['last_page']:``
#        try:
        # filter df where id > last_id
#            df = df[df['id'] > last_id['last_id'][0]]

            # check if the df is empty then break the loop
 #           if df.empty:
#                break

            # Insert the DataFrame into the database table
 #           df.to_sql('customers', engine, if_exists='append', index=False, method="multi")  # Use if_exists='append' instead of 'replace'

            # Update the payload to fetch the next page
  #          payload['page'] += 1
  #          df, meta = fetch_data_from_api(url, token=jwt, payload=payload)
  #          df['membership_vehicle'] = df['membership_vehicle'].astype(str)
  #          df['update_log'] = df['update_log'].astype(str)
   #         sleep_time = random.randint(2, 5)
   #         time.sleep(sleep_time)
   #     except Exception as e:
  #          print(f"Error: {e}")
 #           df.info()
#            df


