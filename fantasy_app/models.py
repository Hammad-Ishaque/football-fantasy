from django.db import models
from django.contrib.auth.models import User
import uuid


class AbstractModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Team(AbstractModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    capital = models.DecimalField(max_digits=10, decimal_places=2, default=5000000)
    total_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def calculate_total_value(self):
        self.total_value = sum(player.value for player in self.players.all())
        self.save()


class Player(AbstractModel):
    class Position(models.TextChoices):
        GOALKEEPER = 'GK', 'Goalkeeper'
        DEFENDER = 'DEF', 'Defender'
        MIDFIELDER = 'MID', 'Midfielder'
        ATTACKER = 'ATT', 'Attacker'

    name = models.CharField(max_length=255)
    position = models.CharField(choices=Position.choices)
    value = models.DecimalField(max_digits=10, decimal_places=2, default=1000000)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, related_name='players')
    is_for_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)


class Transfer(AbstractModel):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sold_players')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bought_players')
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)


class Transaction(AbstractModel):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buyer_history')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_history')
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
