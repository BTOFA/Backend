from django.contrib.auth.models import Group, AnonymousUser
from django.contrib.auth import authenticate
from .models import User, UserOperation, TokenSeries, PackOfTokens, Token
from .operations import op_emit_token, op_get_balance, op_expire_token, op_buy_token, op_emit_currency, op_approve_user, op_create_account
from rest_framework import viewsets
from rest_framework import permissions
from backend.restapi.serializers import UserSerializer, UserInfoSerializer, UserOperationSerializer, TokenSeriesSerializer
from rest_framework.authtoken.models import Token as AuthToken
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from datetime import datetime, timedelta
import pytz


def get_series_datetime(token_series):
    expiration_date = token_series.expiration_datetime.date()
    expiration_time = token_series.expiration_datetime.time()
    return datetime(
        expiration_date.year,
        expiration_date.month,
        expiration_date.day,
        expiration_time.hour,
        expiration_time.minute,
        expiration_time.second,
    )


def check_packs(user):
    for pack in PackOfTokens.objects.filter(user=user):
        expiration_datetime = get_series_datetime(pack.token_series)
        if datetime.now() > expiration_datetime:
            op_expire_token(pack.left_id, pack.right_id)
            pack.delete()


@api_view(["POST"])
def register_user(request):
    # TODO validate wallet
    if ("wallet" not in request.data) or ("password" not in request.data):
        return Response({"status": "error", "reason": "invalid request"}, status=400)
    true_wallet, private_key = op_create_account(request.data["wallet"])
    user = User.objects.create_user(request.data["wallet"], request.data["password"])
    user.true_wallet, user.private_key = true_wallet, private_key
    user.save()
    op_approve_user(user.true_wallet, user.private_key)
    auth_token = AuthToken.objects.create(user=user)
    return Response({"status": "ok", "auth_token": auth_token.key})


@api_view(["POST", "GET"])
def auth_by_pass(request):
    if ("wallet" not in request.data) or ("password" not in request.data):
        return Response({"status": "error", "reason": "invalid request"}, status=400)
    user = authenticate(wallet=request.data["wallet"], password=request.data["password"])
    check_packs(user)
    if user is None:
         return Response({"status": "error", "reason": "invalid credentials"})
    auth_token = AuthToken.objects.get_or_create(user=user)[0]
    return Response({"status": "ok", "auth_token": auth_token.key})


@api_view(["GET"])
def auth(request):
    user = request.user
    if user is None:
        Response({"status": "error", "reason": "Not authed"}, status=400)
    check_packs(user)
    return Response({"status": "ok", "authed": True})


@api_view(["POST"])
def add_balance(request):
    user = request.user
    if user is None:
        Response({"status": "error", "reason": "Not authed"}, status=400)
    check_packs(user)
    if "plus" not in request.data:
        return Response({"status": "error", "reason": "invalid request"}, status=400)
    
    op_emit_currency(user.true_wallet, int(request.data['plus']))
    
    UserOperation.objects.create(
        user=user,
        op_type="RE",
        desc=request.data["plus"],
    )
    return Response({"status": "ok"})


@api_view(["GET"])
def user_info(request):
    user = request.user
    if user is None:
        Response({"status": "error", "reason": "Not authed"}, status=400)
    check_packs(user)
    serialized_user_info = UserInfoSerializer(user).data
    serialized_user_info["balance"] = op_get_balance(user.true_wallet)
    return Response(serialized_user_info)


@api_view(["GET"])
def user_history(request):
    user = request.user
    if user is None:
        Response({"status": "error", "reason": "Not authed"}, status=400)
    check_packs(user)
    operations = UserOperation.objects.filter(user=user)
    serialized_operations = [UserOperationSerializer(op).data for op in operations]
    return Response({"status": "ok", "history": serialized_operations})


@api_view(["GET"])
def user_packs(request):
    user = request.user
    if user is None:
        Response({"status": "error", "reason": "Not authed"}, status=400)
    check_packs(user)
    user_packs = PackOfTokens.objects.filter(user=user)

    serialized_packs = [{
        "wallet ": user.wallet,
        "token_series": pack.token_series.name,
        "number_of_tokens": pack.number_of_tokens,
        "left_id": pack.left_id,
        "right_id": pack.right_id,
    } for pack in user_packs]
    return Response({"status": "ok", "packs": serialized_packs})


@api_view(["POST"])
def create_token(request):
    user = request.user
    if user is None or not user.is_superuser:
        Response({"status": "error", "reason": "Permission Denied"}, status=403)
    
    Token.objects.create(
        name=request.data["name"],   
    )
    return Response({"status": "ok"})


@api_view(["POST"])
def emit_token(request):
    user = request.user
    
    if user is None or not user.is_superuser:
        Response({"status": "error", "reason": "Permission Denied"}, status=403)
    
    if "name" not in request.data:
        return Response({"status": "error", "reason": "No name"}, status=400)
    
    if "metainfo" not in request.data:
        return Response({"status": "error", "reason": "No metainfo"}, status=400)
    
    if "id" not in request.data:
        return Response({"status": "error", "reason": "No token id"}, status=400)

    if "number_of_tokens" not in request.data:
        return Response({"status": "error", "reason": "No number_of_tokens"}, status=400)
    
    if "cost" not in request.data:
        return Response({"status": "error", "reason": "No number_of_tokens"}, status=400)
    
    if "duration" not in request.data:
        return Response({"status": "error", "reason": "No duration"}, status=400)
    
    token = Token.objects.get(id=int(request.data["id"]))
    number_of_tokens = int(request.data["number_of_tokens"])
    cost = int(request.data["cost"])
    duration = int(request.data["duration"])
    dividends = 50 #percent

    series = TokenSeries.objects.create(
        token=token,
        left_id=token.last_id,
        right_id=token.last_id + number_of_tokens - 1,
        last_id=token.last_id,
        name=request.data["name"],
        number_of_tokens=number_of_tokens,
        cost=cost,
        metainfo=request.data["metainfo"],
        expiration_datetime=(datetime.now() + timedelta(seconds=duration)),
        dividends=dividends,
    )
    
    op_emit_token(tokenid=token.last_id, amount=number_of_tokens, series=series)


    token.last_id += number_of_tokens
    token.save()

    return Response({"status": "ok"})


@api_view(["GET"])
def list_tokens_series(request):
    tokens = TokenSeries.objects.all()
    serialized_tokens = [TokenSeriesSerializer(tk).data for tk in tokens]
    return Response({"status": "ok", "tokens_series": serialized_tokens})


@api_view(["POST"])
def buy_token(request):
    user = request.user

    if user is None:
        Response({"status": "error", "reason": "Not authed"}, status=400)
    check_packs(user)

    if "id" not in request.data:
        return Response({"status": "error", "reason": "No id"}, status=400)
    
    if "number_of_tokens" not in request.data:
        return Response({"status": "error", "reason": "No number_of_tokens"}, status=400)
    
    number_of_tokens = int(request.data["number_of_tokens"])
    token_series_id = int(request.data["id"])
    token_series = TokenSeries.objects.get(id=token_series_id)
    left_id, right_id = token_series.last_id, (token_series.last_id + number_of_tokens - 1)

    if datetime.now() > get_series_datetime(token_series):
        return Response({"status": "error", "reason": "Series has expired"}, status=400)
    
    if op_get_balance(user.wallet) < token_series.cost * number_of_tokens:
        return Response({"status": "error", "reason": "Insufficient balance"}, status=400)
    
    if number_of_tokens > token_series.number_of_tokens:
        return Response({"status": "error", "reason": "Too many tokens"}, status=400)
    
    op_buy_token(user.true_wallet, user.private_key, left_id, right_id, number_of_tokens * token_series.cost)

    PackOfTokens.objects.create(
        user=user,
        token_series=token_series,
        number_of_tokens=number_of_tokens,
        left_id=left_id,
        right_id=right_id,
    )
    token_series.number_of_tokens -= number_of_tokens
    token_series.last_id = right_id + 1
    token_series.save()
    UserOperation.objects.create(
        user=user,
        op_type='PU',
        desc=str(number_of_tokens),
    )
    return Response({"status": "ok"})



class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
