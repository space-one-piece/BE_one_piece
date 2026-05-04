from django.contrib import admin
from django.contrib.admin.exceptions import NotRegistered

from apps.users.models.models import SocialUser, User, UserWithdrawal

from .social_user_admin import SocialUserAdmin
from .user_admin import UserAdmin
from .withdrawal_admin import UserWithdrawalAdmin

try:
    admin.site.unregister(User)
except NotRegistered:
    pass
admin.site.register(User, UserAdmin)

try:
    admin.site.unregister(SocialUser)
except NotRegistered:
    pass
admin.site.register(SocialUser, SocialUserAdmin)

try:
    admin.site.unregister(UserWithdrawal)
except NotRegistered:
    pass
admin.site.register(UserWithdrawal, UserWithdrawalAdmin)
