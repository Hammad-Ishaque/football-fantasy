from decimal import Decimal

from django.test import TestCase

from fantasy_app.tests.factories import PlayerFactory
from fantasy_app.tests.factories import TeamFactory
from fantasy_app.tests.factories import TransactionFactory
from fantasy_app.tests.factories import TransferFactory
from fantasy_app.tests.factories import UserFactory


class TeamPlayerTransferTestCase(TestCase):

    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.user2 = UserFactory()

        self.team1 = TeamFactory(user=self.user1)
        self.team2 = TeamFactory(user=self.user2)

        self.player1 = PlayerFactory(value=Decimal('2000000'), team=self.team1)
        self.player2 = PlayerFactory(value=Decimal('1500000'), team=self.team1)

        self.player3 = PlayerFactory(value=Decimal('1000000'), team=self.team2)

    def test_team_initial_capital(self) -> None:
        self.assertEqual(self.team1.capital, Decimal('5000000'))
        self.assertEqual(self.team2.capital, Decimal('5000000'))

    def test_calculate_total_value(self) -> None:
        self.team1.calculate_total_value()
        self.assertEqual(self.team1.total_value, Decimal('3500000'))

    def test_player_default_value(self) -> None:
        self.assertEqual(self.player1.value, Decimal('2000000'))
        self.assertEqual(self.player3.value, Decimal('1000000'))

    def test_transfer_creation(self) -> None:
        """Test if transfer creation updates player team and capital correctly"""
        self.player1.is_for_sale = True
        self.player1.sale_price = Decimal('2500000')
        self.player1.save()

        TransferFactory(
            seller=self.user1,
            buyer=self.user2,
            player=self.player1,
            sale_price=Decimal('2500000'),
        )

        self.player1.team = self.team2
        self.player1.save()

        self.assertEqual(self.player1.team, self.team2)

        self.team1.capital += Decimal('2500000')
        self.team2.capital -= Decimal('2500000')

        self.assertEqual(self.team1.capital, Decimal('7500000'))
        self.assertEqual(self.team2.capital, Decimal('2500000'))

    def test_transaction_creation(self) -> None:
        """Test if transaction is recorded after a player transfer"""
        TransferFactory(
            seller=self.user1,
            buyer=self.user2,
            player=self.player2,
            sale_price=Decimal('1800000'),
        )

        transaction = TransactionFactory(
            buyer=self.user2,
            seller=self.user1,
            player=self.player2,
            amount=Decimal('1800000'),
        )

        self.assertEqual(transaction.buyer, self.user2)
        self.assertEqual(transaction.seller, self.user1)
        self.assertEqual(transaction.player, self.player2)
        self.assertEqual(transaction.amount, Decimal('1800000'))

    def test_multiple_players_transfer(self) -> None:
        """Test transferring multiple players between teams and updating total team values"""
        player4 = PlayerFactory(value=Decimal('1000000'), team=self.team1)

        TransferFactory(
            seller=self.user1,
            buyer=self.user2,
            player=player4,
            sale_price=Decimal('1200000'),
        )

        player4.team = self.team2
        player4.save()

        self.team1.calculate_total_value()
        self.team2.calculate_total_value()

        self.assertEqual(self.team1.total_value, Decimal('3500000'))
        self.assertEqual(self.team2.total_value, Decimal('2000000'))

    def test_transfer_active_flag(self) -> None:
        """Test that a transfer becomes inactive once completed"""
        transfer = TransferFactory(
            seller=self.user1,
            buyer=self.user2,
            player=self.player2,
            sale_price=Decimal('1500000'),
        )

        transfer.active = False
        transfer.save()

        self.assertFalse(transfer.active)
