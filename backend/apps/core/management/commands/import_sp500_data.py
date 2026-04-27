from decimal import Decimal, InvalidOperation

import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.core.models import PriceHistory, Ticker


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    return df


def _pick_column(columns, candidates):
    for c in candidates:
        if c in columns:
            return c
    return None


def _to_decimal(value):
    if pd.isna(value):
        return None
    try:
        d = Decimal(str(value).strip())
        if not d.is_finite():
            return None
        return d
    except (InvalidOperation, TypeError, ValueError):
        return None


class Command(BaseCommand):
    help = "Fast import S&P500 companies + stocks CSV into Ticker and PriceHistory"

    def add_arguments(self, parser):
        parser.add_argument("--companies", type=str, required=True, help="Path to sp500_companies.csv")
        parser.add_argument("--stocks", type=str, required=True, help="Path to sp500_stocks.csv")
        parser.add_argument("--chunksize", type=int, default=50000, help="CSV chunk size for stocks import")
        parser.add_argument("--batch-size", type=int, default=5000, help="DB batch size for bulk_create")

    def handle(self, *args, **options):
        companies_path = options["companies"]
        stocks_path = options["stocks"]
        chunksize = options["chunksize"]
        batch_size = options["batch_size"]

        # 1) Import companies + ensure ticker metadata
        self._import_companies(companies_path, batch_size=batch_size)

        # 2) Fast bulk import stocks in chunks
        imported, skipped = self._import_stocks_fast(
            stocks_path=stocks_path,
            chunksize=chunksize,
            batch_size=batch_size,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Imported {imported} price rows (new rows), skipped {skipped} invalid rows."
            )
        )
        self.stdout.write(
            "Note: importer uses bulk_create(ignore_conflicts=True). "
            "Existing rows are kept as-is for speed."
        )

    def _import_companies(self, companies_path: str, batch_size: int):
        try:
            companies_df = pd.read_csv(companies_path)
        except Exception as exc:
            raise CommandError(f"Failed to read companies CSV: {exc}")

        companies_df = _normalize_columns(companies_df)
        cols = set(companies_df.columns)

        symbol_col = _pick_column(cols, ["symbol", "ticker"])
        name_col = _pick_column(cols, ["security", "name", "company", "company_name"])
        sector_col = _pick_column(cols, ["gics_sector", "sector"])
        exchange_col = _pick_column(cols, ["exchange"])

        if not symbol_col:
            raise CommandError("Could not find symbol/ticker column in companies CSV.")

        self.stdout.write("Importing companies metadata...")

        to_create = []
        updates = []
        existing = {t.symbol: t for t in Ticker.objects.all().only("id", "symbol", "name", "sector", "exchange")}

        for row in companies_df.itertuples(index=False):
            data = row._asdict() if hasattr(row, "_asdict") else {}
            symbol_raw = data.get(symbol_col)
            if pd.isna(symbol_raw):
                continue

            symbol = str(symbol_raw).strip().upper()
            if not symbol or symbol == "NAN":
                continue

            name = "" if name_col is None or pd.isna(data.get(name_col)) else str(data.get(name_col)).strip()
            sector = "" if sector_col is None or pd.isna(data.get(sector_col)) else str(data.get(sector_col)).strip()
            exchange = "" if exchange_col is None or pd.isna(data.get(exchange_col)) else str(data.get(exchange_col)).strip()

            if symbol in existing:
                t = existing[symbol]
                changed = False
                if name and t.name != name:
                    t.name = name
                    changed = True
                if sector and t.sector != sector:
                    t.sector = sector
                    changed = True
                if exchange and t.exchange != exchange:
                    t.exchange = exchange
                    changed = True
                if changed:
                    updates.append(t)
            else:
                to_create.append(Ticker(symbol=symbol, name=name, sector=sector, exchange=exchange))

        if to_create:
            Ticker.objects.bulk_create(to_create, batch_size=batch_size, ignore_conflicts=True)

        if updates:
            Ticker.objects.bulk_update(updates, ["name", "sector", "exchange"], batch_size=batch_size)

    def _import_stocks_fast(self, stocks_path: str, chunksize: int, batch_size: int):
        # Build ticker lookup once; add missing symbols per chunk when needed.
        ticker_map = {t.symbol: t.id for t in Ticker.objects.all().only("id", "symbol")}

        imported_total = 0
        skipped_total = 0
        chunk_no = 0

        try:
            reader = pd.read_csv(stocks_path, chunksize=chunksize)
        except Exception as exc:
            raise CommandError(f"Failed to read stocks CSV: {exc}")

        self.stdout.write("Importing stocks in chunks (fast mode)...")

        for chunk in reader:
            chunk_no += 1
            chunk = _normalize_columns(chunk)
            cols = set(chunk.columns)

            symbol_col = _pick_column(cols, ["symbol", "ticker"])
            date_col = _pick_column(cols, ["date"])
            open_col = _pick_column(cols, ["open"])
            high_col = _pick_column(cols, ["high"])
            low_col = _pick_column(cols, ["low"])
            close_col = _pick_column(cols, ["close"])
            volume_col = _pick_column(cols, ["volume"])

            required = [symbol_col, date_col, open_col, high_col, low_col, close_col, volume_col]
            if any(v is None for v in required):
                raise CommandError(
                    "Could not find required columns in stocks CSV. Need: symbol/ticker, date, open, high, low, close, volume."
                )

            # Ensure tickers in this chunk exist
            chunk_symbols = (
                chunk[symbol_col]
                .dropna()
                .astype(str)
                .str.strip()
                .str.upper()
            )
            missing_symbols = sorted(set(s for s in chunk_symbols if s and s != "NAN" and s not in ticker_map))
            if missing_symbols:
                Ticker.objects.bulk_create(
                    [Ticker(symbol=s) for s in missing_symbols],
                    batch_size=batch_size,
                    ignore_conflicts=True,
                )
                # Refresh only missing symbols
                for t in Ticker.objects.filter(symbol__in=missing_symbols).only("id", "symbol"):
                    ticker_map[t.symbol] = t.id

            # Convert date once vectorized
            chunk[date_col] = pd.to_datetime(chunk[date_col], errors="coerce").dt.date

            to_insert = []

            for row in chunk.itertuples(index=False):
                data = row._asdict() if hasattr(row, "_asdict") else {}

                symbol_raw = data.get(symbol_col)
                if pd.isna(symbol_raw):
                    skipped_total += 1
                    continue

                symbol = str(symbol_raw).strip().upper()
                if not symbol or symbol == "NAN":
                    skipped_total += 1
                    continue

                ticker_id = ticker_map.get(symbol)
                if not ticker_id:
                    skipped_total += 1
                    continue

                date_val = data.get(date_col)
                if pd.isna(date_val):
                    skipped_total += 1
                    continue

                open_v = _to_decimal(data.get(open_col))
                high_v = _to_decimal(data.get(high_col))
                low_v = _to_decimal(data.get(low_col))
                close_v = _to_decimal(data.get(close_col))

                if None in (open_v, high_v, low_v, close_v):
                    skipped_total += 1
                    continue

                volume_raw = data.get(volume_col)
                if pd.isna(volume_raw):
                    volume_v = 0
                else:
                    try:
                        volume_v = int(float(volume_raw))
                    except Exception:
                        volume_v = 0

                to_insert.append(
                    PriceHistory(
                        ticker_id=ticker_id,
                        date=date_val,
                        open=open_v,
                        high=high_v,
                        low=low_v,
                        close=close_v,
                        volume=volume_v,
                    )
                )

            if to_insert:
                # Requires unique constraint (ticker, date), which your model already has.
                with transaction.atomic():
                    PriceHistory.objects.bulk_create(
                        to_insert,
                        batch_size=batch_size,
                        ignore_conflicts=True,
                    )
                imported_total += len(to_insert)

            self.stdout.write(
                f"Chunk {chunk_no}: prepared {len(to_insert)} rows, cumulative prepared {imported_total}, skipped {skipped_total}"
            )

        return imported_total, skipped_total
