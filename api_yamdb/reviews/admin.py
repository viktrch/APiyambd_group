from django.contrib import admin
from .models import Categories, Genre, Title, Review, Comment, GenreTitle

admin.site.register(Categories)
admin.site.register(Genre)
admin.site.register(Title)
admin.site.register(Review)
admin.site.register(Comment)
admin.site.register(GenreTitle)
