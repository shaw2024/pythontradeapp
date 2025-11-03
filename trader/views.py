from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from pathlib import Path
from decimal import Decimal

from .models import Account, Position, Trade
from .utils import load_series
from django.conf import settings


REPO_ROOT = Path(settings.BASE_DIR)


def ensure_account():
    acct, _ = Account.objects.get_or_create(id=1, defaults={"name": "Default Account", "cash": Decimal("100000.00")})
    return acct


def index(request):
    symbol = request.GET.get("symbol", "AAPL")
    account = ensure_account()

    dates, closes = load_series(symbol, REPO_ROOT)
    latest_price = closes[-1] if closes else None

    # portfolio summary
    positions = account.positions.all()
    trades = account.trades.order_by("-timestamp")[:50]

    # mark-to-market value
    total_positions_value = 0
    for p in positions:
        price = latest_price or 0
        total_positions_value += p.quantity * price

    context = {
        "symbol": symbol,
        "dates": dates,
        "closes": closes,
        "latest_price": latest_price,
        "account": account,
        "positions": positions,
        "trades": trades,
        "positions_value": total_positions_value,
    }
    return render(request, "trader/index.html", context)


def trade_action(request):
    if request.method != "POST":
        return redirect(reverse("trader:index"))

    action = request.POST.get("action")
    symbol = request.POST.get("symbol")
    qty = int(request.POST.get("quantity", 0))
    account = ensure_account()
    dates, closes = load_series(symbol, REPO_ROOT)
    price = Decimal(str(closes[-1])) if closes else Decimal("0")

    if action == "buy":
        cost = price * qty
        if account.cash < cost:
            messages.error(request, "Insufficient cash for this purchase.")
            return redirect(f"?symbol={symbol}")
        # update or create position
        pos, _ = Position.objects.get_or_create(account=account, symbol=symbol, defaults={"quantity": 0, "avg_price": 0})
        new_total_qty = pos.quantity + qty
        if new_total_qty > 0:
            new_avg = ((Decimal(pos.avg_price) * pos.quantity) + (price * qty)) / new_total_qty
        else:
            new_avg = Decimal("0")
        pos.quantity = new_total_qty
        pos.avg_price = new_avg
        pos.save()
        account.cash = Decimal(account.cash) - cost
        account.save()
        Trade.objects.create(account=account, symbol=symbol, side="BUY", quantity=qty, price=price)
        messages.success(request, f"Bought {qty} {symbol} @ {price}")

    elif action == "sell":
        try:
            pos = Position.objects.get(account=account, symbol=symbol)
        except Position.DoesNotExist:
            messages.error(request, "No shares to sell.")
            return redirect(f"?symbol={symbol}")
        if qty > pos.quantity:
            messages.error(request, "Not enough shares to sell.")
            return redirect(f"?symbol={symbol}")
        proceeds = price * qty
        pos.quantity = pos.quantity - qty
        if pos.quantity == 0:
            pos.avg_price = 0
        pos.save()
        account.cash = Decimal(account.cash) + proceeds
        account.save()
        Trade.objects.create(account=account, symbol=symbol, side="SELL", quantity=qty, price=price)
        messages.success(request, f"Sold {qty} {symbol} @ {price}")

    return redirect(f"{reverse('trader:index')}?symbol={symbol}")


def reset_action(request):
    if request.method != "POST":
        return redirect(reverse("trader:index"))
    # reset account, trades, positions
    Account.objects.all().delete()
    Position.objects.all().delete()
    Trade.objects.all().delete()
    ensure_account()
    messages.success(request, "Reset complete. Account restored to default cash.")
    return redirect(reverse("trader:index"))
from django.shortcuts import render

# Create your views here.
