from django.db import models
import datetime
from log.models import Log


'''Strategy model, where strategy is basically what to do 
when getting the 'good' and 'bad' analytics result,
how much of shares can be in the briefcase at the same time and
how much shares can we borrow'''
class Strategy(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='Strategy name',
        unique=True
    )
    long_limit = models.PositiveSmallIntegerField(
        verbose_name='Shares amount limit to store'
    )
    short_limit = models.SmallIntegerField(
        verbose_name='Shares amount limit to borrow'
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        db_index=True,
    )

    # Decides whether it to buy or to sell the share
    def buy_or_sell(self, portfolio_image, index, date):
        for delta in range(3):
            quote = portfolio_image.shares[index].origin.quotes[(
                    date + datetime.timedelta(days=delta)
            ).strftime('%Y-%m-%d')]['close']
            current = portfolio_image.shares[index].origin.quotes[
                (date + datetime.timedelta(days=3)).strftime('%Y-%m-%d')
            ]['close']
            if current > quote and portfolio_image.shares[index].amount + 1 <= self.long_limit\
                    and portfolio_image.balance >= current:
                portfolio_image.shares[index].amount += 1
                portfolio_image.balance -= current
            elif current < quote and portfolio_image.shares[index].amount - 1 >= self.short_limit:
                portfolio_image.shares[index].amount -= 1
                portfolio_image.balance += current
        portfolio_image.set_cost((date + datetime.timedelta(days=3)).strftime('%Y-%m-%d'))
        return portfolio_image

    def get_results(self):
        logs = Log.objects.filter(
            strategy=self
        )
        if logs:
            success = 0
            for log in logs:
                success = success + 1 \
                    if log.price_deltas['balance']['currency'] >= 0 \
                    else success
            return {
                'success': {
                    'amount': success,
                    'percent': round(success / len(logs), 2) * 100,
                },
                'fail': {
                    'amount': len(logs) - success,
                    'percent': round(1 - success / len(logs), 2) * 100,
                }
            }
        else:
            return None

    def save(self, **kwargs):
        if not self.slug or self.slug != self.name.replace(' ', '_').lower():
            self.slug = self.name.replace(' ', '_').lower()
        super(Strategy, self).save()
