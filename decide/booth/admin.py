from django.contrib import admin

from .models import SuggestingForm

class SuggestingFormAdmin(admin.ModelAdmin):
    list_display = ('title', 'user_id', 'send_date')
    list_filter = ('user_id', 'send_date')
    search_fields = ('user_id', 'send_date')
    readonly_fields = ('user_id', 'send_date', 'title', 'suggesting_date', 'content')

admin.site.register(SuggestingForm, SuggestingFormAdmin)