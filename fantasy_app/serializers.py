from typing import Optional

from django.contrib.auth.models import User
from django.db.models import Model

from rest_framework import serializers

from fantasy_app.models import Player
from fantasy_app.models import Team
from fantasy_app.models import Transaction


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data: dict) -> Model:
        user, _ = User.objects.get_or_create(
            email=validated_data['email'],
            defaults={
                'username': validated_data['username'],
                'password': validated_data['password'],
            },
        )
        Team.objects.get_or_create(user=user, defaults={'name': f"{user.username}'s Team"})
        return user


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'name', 'position', 'value', 'team', 'is_for_sale', 'sale_price']


class TeamSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True, read_only=True)

    class Meta:
        model = Team
        fields = ['name', 'total_value', 'players']


class UserProfileSerializer(serializers.ModelSerializer):
    team = TeamSerializer()

    class Meta:
        model = User
        fields = ['username', 'email', 'capital', 'team']


class PlayerTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'is_for_sale', 'sale_price']
        read_only_fields = ['id']

    def validate(self, data: dict) -> Optional[dict]:
        if data['is_for_sale'] and not data.get('sale_price'):
            raise serializers.ValidationError('Sale price must be provided when listing a player for sale.')
        return data


class TransactionSerializer(serializers.ModelSerializer):
    player_name = serializers.CharField(source='player.name', read_only=True)
    buyer_username = serializers.CharField(source='buyer.username', read_only=True)
    seller_username = serializers.CharField(source='seller.username', read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'player_name', 'buyer_username', 'seller_username', 'amount', 'transaction_date']
