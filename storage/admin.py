from django.contrib import admin

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import UserFile


class UserFileAdmin(admin.ModelAdmin):
    list_display = ('original_name', 'user', 'size', 'upload_date', 'download_link')
    list_filter = ('user', 'upload_date')
    search_fields = ('original_name', 'user__username')
    readonly_fields = ('original_name', 'size', 'upload_date', 'last_download', 'unique_identifier')

    def download_link(self, obj):
        url = reverse('admin-download-file', args=[obj.id])
        return format_html('<a href="{}">Скачать</a>', url)

    download_link.short_description = 'Скачать'


admin.site.register(UserFile, UserFileAdmin)