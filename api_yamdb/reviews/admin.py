from django.contrib import admin

from .models import User, Genre, Title, GenreTitle, Comment, Category, Review

admin.site.register(User)
admin.site.register(Genre)
admin.site.register(Title)
admin.site.register(GenreTitle)
admin.site.register(Comment)
admin.site.register(Category)
admin.site.register(Review)
