from django.contrib import admin

from weather.models import SearchHistory


@admin.register(SearchHistory)
class ContactsAdmin(admin.ModelAdmin):
    list_display = ["user", "user_ip", "city", "count"]
    list_editable = ["city"]

