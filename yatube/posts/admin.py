from django.contrib import admin
from .models import Post, Group, Follow, Comment


class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'created', 'author', 'group')
    search_fields = ('text',)
    list_filter = ('created',)
    list_editable = ('group', )
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)
admin.site.register(Group)
admin.site.register(Follow)
admin.site.register(Comment)
