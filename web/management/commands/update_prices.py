# web/management/commands/update_prices.py

import yfinance as yf
from django.core.management.base import BaseCommand
from web.models import StockHolding, PriceData
from decimal import Decimal

class Command(BaseCommand):
    help = 'Updates the stock prices for all holdings from Yahoo Finance'

    def handle(self, *args, **options):
        self.stdout.write("Starting price update process...")

        # Get all unique tickers from the current stock holdings
        tickers = StockHolding.objects.values_list('ticker', flat=True).distinct()

        if not tickers:
            self.stdout.write("No stock holdings to update.")
            return

        self.stdout.write(f"Found {len(tickers)} unique tickers to update: {', '.join(tickers)}")

        for ticker_symbol in tickers:
            try:
                # Download EOD data for the most recent trading day
                stock = yf.Ticker(ticker_symbol)
                hist = stock.history(period="1d")

                if hist.empty:
                    self.stdout.write(self.style.WARNING(f"Could not get historical data for {ticker_symbol}"))
                    continue

                # The last available closing price is our EOD price
                eod_price = hist['Close'].iloc[-1]
                company_name = stock.info.get('longName', ticker_symbol)

                # Use update_or_create to either update an existing record or create a new one
                price_obj, created = PriceData.objects.update_or_create(
                    ticker=ticker_symbol,
                    defaults={
                        'price': Decimal(eod_price),
                        'company_name': company_name
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created price cache for {ticker_symbol}: ${eod_price:.2f}"))
                else:
                    self.stdout.write(self.style.SUCCESS(f"Updated price for {ticker_symbol}: ${eod_price:.2f}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error updating {ticker_symbol}: {e}"))

        self.stdout.write("Price update process finished.")