from django.urls import path

from fantasy_app.views import PlayerBuyView
from fantasy_app.views import PlayerDetailView
from fantasy_app.views import PlayerListView
from fantasy_app.views import PlayerTransferUpdateView
from fantasy_app.views import TeamDetailView
from fantasy_app.views import TeamRecalculateValueView
from fantasy_app.views import TransactionListView
from fantasy_app.views import UserProfileView
from fantasy_app.views import UserRegistrationView
from fantasy_app.views import UserTransactionListView


urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('team/', TeamDetailView.as_view(), name='team-detail'),
    path('team/recalculate/', TeamRecalculateValueView.as_view(), name='team-recalculate-value'),
    path('players/', PlayerListView.as_view(), name='player-list'),
    path('players/<str:pk>/', PlayerDetailView.as_view(), name='player-detail'),
    path('players/<str:pk>/transfer/', PlayerTransferUpdateView.as_view(), name='player-transfer'),
    path('players/<str:player_id>/buy/', PlayerBuyView.as_view(), name='player-buy'),
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),
    path('my/transactions/', UserTransactionListView.as_view(), name='user-transaction-list'),
]
