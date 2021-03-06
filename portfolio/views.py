import datetime
import re
from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from log.models import Log
from log.serializers import LogSerializer
from portfolio.models import Portfolio
from portfolio.serializers import PortfolioSerializer
from quotes.models import Stock, Quotes


class PortfolioAPIView(
    generics.CreateAPIView,
    generics.RetrieveUpdateDestroyAPIView
):
    def get(self, request, *args, **kwargs):  # detail
        portfolio = Portfolio.objects.get(
            slug=kwargs.get('slug')
        )
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return Response(
                data={
                    'portfolio': PortfolioSerializer(portfolio).data,
                    'logs': LogSerializer(
                        Log.objects.filter(portfolio=portfolio),
                        many=True,
                    ).data
                },
                status=200
            )
        else:
            return render(
                request=request,
                template_name='index.html',
            )

    def post(self, request, *args, **kwargs):  # create
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            data = {key: request.data.get(key) for key in request.data}
            serializer = PortfolioSerializer(data={
                'name': data.get('name').strip().capitalize(),
                'slug': re.sub(r'[.\- ]+', '_', data.get('name').strip().lower()),
                'balance': data.get('balance')
            })
            serializer.is_valid(raise_exception=True)
            return Response(
                data={
                    'portfolio': serializer.create()
                },
                status=200
            )
        else:
            pass

    def patch(self, request, *args, **kwargs):  # update
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            # Getting data from client
            data = {key: request.data.get(key) for key in request.data}
            serializer = PortfolioSerializer(data={
                'name': data.get('name').strip().capitalize(),
                'slug': re.sub(r'[.\- ]+', '_', data.get('name').strip().lower()),
                'balance': data.get('balance'),
                'last_updated': datetime.datetime.now(),
            } if re.sub(
                r'[.\- ]+', '_', data.get('name').strip().lower()
            ) != kwargs.get('slug') else {
                'balance': data.get('balance'),
                'last_updated': datetime.datetime.now(),
            }, partial=True)
            serializer.is_valid(raise_exception=True)
            return Response(
                data={
                    'portfolio': serializer.update(kwargs.get('slug'))
                },
                status=200
            )
        else:
            pass

    def put(self, request, *args, **kwargs):  # manage stocks
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            # Add, change amount of or delete stocks
            portfolio = Portfolio.objects.get(
                slug=kwargs.get('slug'),
            )
            if kwargs.get('type') == 'add':
                if not portfolio.stocks.filter(origin__symbol=request.data.get('symbol')).exists():
                    stock = Stock.objects.create(
                        origin=Quotes.objects.get(
                            symbol=request.data.get('symbol')
                        ),
                        amount=1,
                    )
                    portfolio.stocks.add(stock)
                    portfolio.save()
            elif kwargs.get('type') == 'change_amount':
                errors = {}
                try:
                    amount = int(request.data.get('amount'))
                    if amount <= 0:
                        errors['amount'] = ['Stocks amount must be positive value.']
                except ValueError:
                    errors['amount'] = ['Invalid value format.']
                if errors:
                    return Response(
                        data=errors,
                        status=400,
                    )
                else:
                    portfolio.stocks.filter(
                        origin=Quotes.objects.get(
                            symbol=request.data.get('symbol')
                        )
                    ).update(
                        amount=request.data.get('amount')
                    )
                    portfolio.last_updated = datetime.datetime.now()
                    portfolio.save()
            elif kwargs.get('type') == 'delete':
                portfolio.stocks.get(
                    origin=Quotes.objects.get(
                        symbol=request.data.get('symbol')
                    ),
                ).delete()
            return Response(
                data={
                    'portfolio': PortfolioSerializer(portfolio).data
                },
                status=200
            )
        else:
            pass

    def delete(self, request, *args, **kwargs):  # delete
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            Portfolio.objects.get(
                slug=kwargs.get('slug')
            ).delete()
            return Response(
                data={},
                status=200
            )
        else:
            pass


# Shows list of all portfolios
class PortfolioListAPIView(
    generics.ListAPIView
):
    def get(self, request, *args, **kwargs):  # list
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return Response(
                data={
                    'portfolios': PortfolioSerializer(
                        Portfolio.objects.order_by('-last_updated', '-created'),
                        many=True
                    ).data
                },
                status=200,
            )
        else:
            pass
        return render(
            template_name='index.html',
            request=request,
        )
