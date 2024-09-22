from django.contrib.auth.models import User

import factory

from fantasy_app.models import Player
from fantasy_app.models import Team
from fantasy_app.models import Transaction
from fantasy_app.models import Transfer


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user_{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'password123')


class TeamFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Team

    user = factory.SubFactory(UserFactory)
    capital = factory.LazyFunction(lambda: 5000000)
    total_value = factory.LazyFunction(lambda: 0)


class PlayerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Player

    name = factory.Faker('name')
    position = factory.Faker('random_element', elements=Player.Position.values)
    value = factory.LazyFunction(lambda: 1000000)
    team = factory.SubFactory(TeamFactory)


class TransferFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transfer

    seller = factory.SubFactory(UserFactory)
    buyer = factory.SubFactory(UserFactory)
    player = factory.SubFactory(PlayerFactory)
    sale_price = factory.LazyFunction(lambda: 1500000)
    active = True


class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction

    buyer = factory.SubFactory(UserFactory)
    seller = factory.SubFactory(UserFactory)
    player = factory.SubFactory(PlayerFactory)
    amount = factory.LazyFunction(lambda: 1000000)
