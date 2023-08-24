from django.contrib import admin

from .models import Subscribe, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username',)
    search_fields = ('username', 'email')
    empty_value_display = '-пусто-'


@admin.register(Subscribe)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscrubing')
    search_fields = ('username', 'email')
    empty_value_display = '-пусто-'
