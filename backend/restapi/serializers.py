from django.contrib.auth.models import Group
from rest_framework import serializers
from .models import User, TokenSeries, PackOfTokens

class UserInfoSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    wallet = serializers.CharField(max_length=30)
    is_superuser = serializers.BooleanField()
    is_staff = serializers.BooleanField()
    status = serializers.CharField(max_length=30, default="ok")


class UserOperationSerializer(serializers.Serializer):
    op_type = serializers.CharField(max_length=2)
    desc = serializers.CharField(max_length=30)
    performed = serializers.DateTimeField()


class TokenSeriesSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=30)
    left_id = serializers.IntegerField()
    right_id = serializers.IntegerField()
    last_id = serializers.IntegerField()
    number_of_tokens = serializers.IntegerField()
    cost = serializers.IntegerField()
    metainfo = serializers.CharField(max_length=30)
    created = serializers.DateTimeField()
    expiration_datetime = serializers.DateTimeField()
    dividends = serializers.IntegerField()


class UserSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = User
        fields = ['url', 'wallet']


class PackSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PackOfTokens
        fields = ['url', 'user', ]
