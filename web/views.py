# your_app_name/views.py

from django.shortcuts import render, redirect
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
# import yfinance as yf # This should be commented out or removed if using the new command
from datetime import datetime
from decimal import Decimal

# Add these imports if not already there
from django.contrib.auth.models import User
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from .models import Position, Transaction, StockHolding, PriceData # Ensure PriceData is imported
from collections import defaultdict
# Add new views

# IMPORTANT: Define is_admin HERE, before its first use in any view
def is_admin(user):
    """Check if user is admin"""
    return user.is_staff or user.is_superuser

# Keep existing views
def index(request):
    return render(request, "base.html")

def home(request):
    return render(request, "home.html")


def about(request):
    return render(request, 'about.html')

def investment(request):
    """
    Renders the investment page and calculates portfolio sector allocation for the chart.
    """
    # 1. Create a mapping from each ticker to its industry group.
    # We use a database-agnostic method to get the most recent transaction for each ticker.
    ticker_to_industry = {}
    # Order by ticker, then by date descending to get the most recent first
    all_transactions = Transaction.objects.order_by('ticker', '-transaction_date').values('ticker', 'industry_group')
    
    # This loop ensures we only keep the first (i.e., most recent) entry for each ticker
    for t in all_transactions:
        if t['ticker'] not in ticker_to_industry:
            ticker_to_industry[t['ticker']] = t['industry_group']

    # 2. Get all current holdings and cached prices.
    holdings = StockHolding.objects.all()
    cached_prices = {price.ticker: price.price for price in PriceData.objects.all()}

    # 3. Calculate the total market value for each sector.
    sector_values = defaultdict(float)
    total_portfolio_value = 0.0

    for holding in holdings:
        current_price = cached_prices.get(holding.ticker)
        if not current_price:
            continue # Skip holdings without a cached price

        market_value = float(holding.shares) * float(current_price)
        industry = ticker_to_industry.get(holding.ticker, 'Other') # Default to 'Other' if not found
        
        # ----------- THIS IS THE CORRECTED LINE -----------
        industry_display = dict(Position.INDUSTRY_GROUPS).get(industry, industry)

        sector_values[industry_display] += market_value
        total_portfolio_value += market_value

    # 4. Prepare the data for Chart.js.
    chart_labels = []
    chart_data = []
    if total_portfolio_value > 0:
        # Sort sectors by value for a cleaner chart
        sorted_sectors = sorted(sector_values.items(), key=lambda item: item[1], reverse=True)
        for sector, value in sorted_sectors:
            chart_labels.append(sector)
            percentage = round((value / total_portfolio_value) * 100, 2)
            chart_data.append(percentage)

    context = {
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data)
    }

    return render(request, 'investment.html', context)

def recruitment(request):
    return render(request, 'recruitment.html')

def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        return render(request, "contact.html", {"success": True})
    return render(request, 'contact.html')

def leadership(request):
    """Display leadership team on the website"""
    executives = Position.objects.filter(position_type='EXEC')
    portfolio_managers = Position.objects.filter(position_type='PM').order_by('industry_group')
    senior_analysts = Position.objects.filter(position_type='SA').order_by('industry_group')

    return render(request, 'leadership.html', {
        'executives': executives,
        'portfolio_managers': portfolio_managers,
        'senior_analysts': senior_analysts
    })

def performance(request):
    """Display portfolio performance on the website"""
    holdings = StockHolding.objects.all().order_by('ticker')
    portfolio_data = []
    total_value = 0
    total_cost = 0

    cached_prices = {price_obj.ticker: price_obj for price_obj in PriceData.objects.all()}

    for holding in holdings:
        current_price = 0
        company_name = holding.ticker

        cached_data = cached_prices.get(holding.ticker)

        if cached_data:
            current_price = float(cached_data.price)
            company_name = cached_data.company_name if cached_data.company_name else holding.ticker
        else:
            print(f"WARNING: Price for {holding.ticker} not found in cache.")

        try:
            position_value = float(holding.shares) * current_price
            position_cost = float(holding.shares) * float(holding.cost_basis)
            gain_loss = position_value - position_cost
            gain_loss_pct = (gain_loss / position_cost) * 100 if position_cost > 0 else 0

            total_value += position_value
            total_cost += position_cost

            portfolio_data.append({
                'ticker': holding.ticker,
                'company_name': company_name,
                'shares': holding.shares,
                'cost_basis': holding.cost_basis,
                'current_price': current_price,
                'position_value': position_value,
                'gain_loss': gain_loss,
                'gain_loss_pct': gain_loss_pct
            })
        except Exception as e:
            portfolio_data.append({
                'ticker': holding.ticker,
                'company_name': 'Data unavailable',
                'shares': holding.shares,
                'cost_basis': holding.cost_basis,
                'current_price': 0,
                'position_value': 0,
                'gain_loss': 0,
                'gain_loss_pct': 0
            })

    overall_gain_loss = total_value - total_cost
    overall_gain_loss_pct = (overall_gain_loss / total_cost) * 100 if total_cost > 0 else 0

    return render(request, 'performance.html', {
        'portfolio_data': portfolio_data,
        'total_value': total_value,
        'total_cost': total_cost,
        'overall_gain_loss': overall_gain_loss,
        'overall_gain_loss_pct': overall_gain_loss_pct
    })

# Admin views that require authentication
# These decorators use is_admin, so is_admin must be defined above them.
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard view"""
    return render(request, 'dashboard.html')

@login_required
@user_passes_test(is_admin)
def manage_team(request):
    """View to manage team members"""
    executives = Position.objects.filter(position_type='EXEC')
    portfolio_managers = Position.objects.filter(position_type='PM').order_by('industry_group')
    senior_analysts = Position.objects.filter(position_type='SA').order_by('industry_group')

    return render(request, 'manage_team.html', {
        'executives': executives,
        'portfolio_managers': portfolio_managers,
        'senior_analysts': senior_analysts
    })

@login_required
@user_passes_test(is_admin)
@require_POST
def add_team_member(request):
    """Add a new team member"""
    try:
        name = request.POST.get('name')
        position_type = request.POST.get('position_type')

        new_member = Position(name=name, position_type=position_type)

        if position_type == 'EXEC':
            new_member.exec_role = request.POST.get('exec_role')
        else:
            new_member.industry_group = request.POST.get('industry_group')

        if 'profile_picture' in request.FILES and position_type != 'SA':
            image = request.FILES['profile_picture']
            new_member.profile_picture.save(image.name, image)

        new_member.save()
        return redirect('manage_team')
    except Exception as e:
        return render(request, 'manage_team.html', {'error': str(e)})

@login_required
@user_passes_test(is_admin)
def delete_team_member(request, member_id):
    """Delete a team member"""
    try:
        member = Position.objects.get(id=member_id)

        if member.profile_picture:
            default_storage.delete(member.profile_picture.path)

        member.delete()
        return redirect('manage_team')
    except Exception as e:
        return render(request, 'manage_team.html', {'error': str(e)})

@login_required
@user_passes_test(is_admin)
def manage_portfolio(request):
    transactions = Transaction.objects.all().order_by('-transaction_date')
    holdings_query = StockHolding.objects.all().order_by('ticker')

    transaction_data = []
    for transaction in transactions:
        transaction_data.append({
            'transaction_date': transaction.transaction_date,
            'ticker': transaction.ticker,
            'transaction_type_display': transaction.get_transaction_type_display(),
            'shares': transaction.shares,
            'price': transaction.price,
            'total_price': transaction.price * transaction.shares,
            'created_by': transaction.created_by.get_full_name(),
            'industry_group_display': transaction.get_industry_group_display(),
        })

    holdings_data = []
    for holding in holdings_query:
        holdings_data.append({
            'ticker': holding.ticker,
            'shares': holding.shares,
            'cost_basis': holding.cost_basis,
            'total_holding_cost': holding.cost_basis * holding.shares,
            'last_updated': holding.last_updated,
        })

    context = {
        'transactions': transaction_data,
        'holdings': holdings_data,
        'industry_groups': Position.INDUSTRY_GROUPS,
    }

    if 'success_message' in request.session:
        context['success_message'] = request.session.pop('success_message')

    return render(request, 'manage_portfolio.html', context)

@login_required
@user_passes_test(is_admin)
@require_POST
def add_transaction(request):
    """Add a new stock transaction"""
    try:
        ticker = request.POST.get('ticker').upper()
        transaction_date = datetime.strptime(request.POST.get('transaction_date'), '%Y-%m-%d')
        price = Decimal(request.POST.get('price'))
        transaction_type = request.POST.get('transaction_type')
        shares = Decimal(request.POST.get('shares'))
        industry_group = request.POST.get('industry_group')

        transaction = Transaction(
            ticker=ticker,
            transaction_date=transaction_date,
            price=price,
            transaction_type=transaction_type,
            shares=shares,
            industry_group=industry_group,
            created_by=request.user
        )
        transaction.save()

        holding, created = StockHolding.objects.get_or_create(ticker=ticker,
                                                               defaults={'shares': 0, 'cost_basis': 0})

        if transaction_type == 'BUY':
            if holding.shares == 0:
                holding.cost_basis = price
                holding.shares = shares
            else:
                total_cost = (holding.shares * holding.cost_basis) + (shares * price)
                holding.shares += shares
                holding.cost_basis = total_cost / holding.shares
        elif transaction_type == 'SELL':
            holding.shares -= shares

        if holding.shares <= 0:
            holding.delete()
        else:
            holding.save()

        return redirect('manage_portfolio')
    except Exception as e:
        return render(request, 'manage_portfolio.html', {'error': str(e), 'industry_groups': Position.INDUSTRY_GROUPS})

@login_required
@user_passes_test(is_admin)
@require_POST
def delete_holding(request, ticker):
    """Delete a stock holding"""
    try:
        holding = StockHolding.objects.get(ticker=ticker.upper())
        holding.delete()
        request.session['success_message'] = f"Holding for {ticker.upper()} deleted successfully."
        return redirect('manage_portfolio')
    except StockHolding.DoesNotExist:
        request.session['error'] = f"Holding for {ticker.upper()} not found."
        return redirect('manage_portfolio')
    except Exception as e:
        request.session['error'] = f"Error deleting holding: {str(e)}"
        return redirect('manage_portfolio')

@login_required
@user_passes_test(is_admin)
def get_stock_info(request, ticker):
    """Get current stock info from cached data"""
    try:
        price_data = PriceData.objects.get(ticker=ticker.upper())
        data = {
            'price': float(price_data.price),
            'name': price_data.company_name if price_data.company_name else ticker.upper(),
            'last_updated': price_data.last_updated.strftime('%Y-%m-%d %H:%M:%S'),
            'success': True
        }
    except PriceData.DoesNotExist:
        data = {
            'success': False,
            'message': f'Stock information for {ticker.upper()} not found in cache. It might be a new ticker or data not yet fetched.'
        }
    except Exception as e:
        data = {
            'success': False,
            'message': f'Error fetching stock information from cache: {e}'
        }

    return JsonResponse(data)

# New API Endpoint for Portfolio Updates
def api_key_auth(request):
    expected_api_key = settings.DJANGO_UPLOAD_API_KEY

    if not expected_api_key or expected_api_key == "your-super-secret-fallback-key-for-dev":
        print("WARNING: DJANGO_UPLOAD_API_KEY is not securely configured in settings.py or environment.")
        return False

    api_key_from_header = request.headers.get('X-API-KEY')

    return api_key_from_header == expected_api_key

@csrf_exempt
@require_POST
def api_upload_portfolio(request):
    """
    API endpoint to receive portfolio data (holdings and transactions) from a local script.
    """
    if not api_key_auth(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        data = json.loads(request.body)
        holdings_data = data.get('holdings', [])
        transactions_data = data.get('transactions', [])

        StockHolding.objects.all().delete()
        for item in holdings_data:
            ticker = item.get('Ticker').upper()
            shares = Decimal(str(item.get('Shares', 0)))
            cost_basis = Decimal(str(item.get('Cost Basis', 0)))
            StockHolding.objects.create(ticker=ticker, shares=shares, cost_basis=cost_basis)

        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.filter(is_staff=True).first()
        if not admin_user:
            return JsonResponse({'status': 'error', 'message': 'No admin user found to assign transactions to.'}, status=500)

        transactions_added_count = 0
        for item in transactions_data:
            ticker = item.get('Ticker').upper()
            transaction_date_excel = item.get('Date')
            shares = Decimal(str(item.get('Shares', 0)))
            price = Decimal(str(item.get('Price', 0)))
            transaction_type = item.get('Type')
            industry_group = item.get('Industry Group', 'NONE')

            if isinstance(transaction_date_excel, datetime):
                transaction_date = transaction_date_excel.date()
            else:
                try:
                    transaction_date = datetime.strptime(str(transaction_date_excel), '%Y-%m-%d %H:%M:%S').date()
                except ValueError:
                    try:
                        transaction_date = datetime.strptime(str(transaction_date_excel), '%Y-%m-%d').date()
                    except ValueError:
                        print(f"Skipping transaction for {ticker}: Invalid date format '{transaction_date_excel}'.")
                        continue

            existing_transaction = Transaction.objects.filter(
                ticker=ticker,
                transaction_date=transaction_date,
                shares=shares,
                price=price,
                transaction_type=transaction_type
            ).first()

            if not existing_transaction:
                Transaction.objects.create(
                    ticker=ticker,
                    transaction_date=transaction_date,
                    price=price,
                    transaction_type=transaction_type,
                    shares=shares,
                    industry_group=industry_group,
                    created_by=admin_user
                )
                transactions_added_count += 1
        print(f"Added {transactions_added_count} new transactions.")

        return JsonResponse({'status': 'success', 'message': 'Portfolio data updated successfully!'})
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)