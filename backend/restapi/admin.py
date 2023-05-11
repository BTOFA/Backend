from django.contrib import admin
from .models import TokenSeries, PackOfTokens, User, UserOperation, Token
from django.contrib.auth.admin import UserAdmin

admin.site.register(TokenSeries)
admin.site.register(PackOfTokens)
admin.site.register(User)
admin.site.register(Token)
admin.site.register(UserOperation)
