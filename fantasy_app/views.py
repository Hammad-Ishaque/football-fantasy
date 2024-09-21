from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.db import transaction

from fantasy_app.models import Player
from fantasy_app.models import Transaction
from fantasy_app.serializers import TransactionSerializer
from fantasy_app.serializers import UserRegistrationSerializer
from fantasy_app.serializers import UserProfileSerializer
from fantasy_app.serializers import TeamSerializer
from fantasy_app.serializers import PlayerSerializer
from fantasy_app.serializers import PlayerTransferSerializer


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': serializer.data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user


class TeamDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamSerializer

    def get_object(self):
        return self.request.user.team


class TeamRecalculateValueView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        team = self.request.user.team
        team.calculate_total_value()
        return Response(
            {'status': 'Total value recalculated', 'total_value': team.total_value},
            status=status.HTTP_200_OK,
        )


class PlayerListView(generics.ListAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Player.objects.all()


class PlayerDetailView(generics.RetrieveAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [IsAuthenticated]


class PlayerTransferUpdateView(generics.UpdateAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerTransferSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        player = self.get_object()

        if player.team.user != request.user:
            return Response({"error": "You can only modify players from your own team."}, status=status.HTTP_403_FORBIDDEN)

        return self.partial_update(request, *args, **kwargs)


class PlayerBuyView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, player_id, *args, **kwargs):
        try:
            player = Player.objects.get(id=player_id)
        except Player.DoesNotExist:
            return Response({'error': 'Player not found.'}, status=status.HTTP_404_NOT_FOUND)

        buyer = request.user
        seller = player.team.user

        if not player.is_for_sale:
            return Response({'error': 'Player is not for sale.'}, status=status.HTTP_400_BAD_REQUEST)

        if buyer.capital < player.sale_price:
            return Response({'error': 'Insufficient funds to buy this player.'}, status=status.HTTP_400_BAD_REQUEST)

        buyer.capital -= player.sale_price
        seller.capital += player.sale_price

        # Update player ownership
        old_team = player.team
        player.team = buyer.team
        player.is_for_sale = False
        player.sale_price = None
        try:
            with transaction.atomic():
                player.save()
                buyer.save()
                seller.save()
                old_team.calculate_total_value()
                buyer.team.calculate_total_value()

                Transaction.objects.create(
                    buyer=buyer,
                    seller=seller,
                    player=player,
                    amount=player.sale_price
                )
        except Exception:
            pass

        return Response(status=status.HTTP_200_OK)


class TransactionListView(generics.ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.all().order_by('-transaction_date')


class UserTransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.filter(buyer=user).union(
            Transaction.objects.filter(seller=user)
        ).order_by('-transaction_date')
