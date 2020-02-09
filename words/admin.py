from django.contrib import admin
from .models import Words, Profile, UserOldWords, GroupOfWords

# Register your models here.
admin.site.register(Words)
admin.site.register(Profile)
admin.site.register(UserOldWords)
admin.site.register(GroupOfWords)