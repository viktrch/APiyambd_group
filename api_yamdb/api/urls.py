from django.urls import include, path
from rest_framework import routers

from .views import (CategoriesListCreateDestroyApiView, CommentViewSet,
                    GenresListCreateDestroyApiView, ReviewViewSet,
                    SignupViewSet, TitlesListCreateDestroyRetriveApiView,
                    TokenViewSet, UsersDetailRegViewSet, UsersListRegViewSet,
                    UsersRetrieveUpdateApiView)

app_name = 'api'

v1_router = routers.DefaultRouter()

v1_router.register(r'categories',
                   CategoriesListCreateDestroyApiView,
                   basename='categories'
                   )
v1_router.register(r'genres',
                   GenresListCreateDestroyApiView,
                   basename='genres'
                   )
v1_router.register(r'titles',
                   TitlesListCreateDestroyRetriveApiView,
                   basename='titles'
                   )

v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet, basename='reviews'
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments'
)

auth_endpoints = [
    # Эндпойнты для регистрации и получения токена.
    path('signup/', SignupViewSet.as_view(), name='signup'),
    path('token/', TokenViewSet.as_view(), name='token_create'),
]

users_endpoint = [
    # Эндпоинт для получения и изменения данных своей учетной записи.
    path(
        'me/',
        UsersRetrieveUpdateApiView.as_view(),
        name='users_me'
    ),

    # Эндпоинты для администрирования пользователей.
    path('', UsersListRegViewSet.as_view(), name='users_list'),

    path(
        '<username>/',
        UsersDetailRegViewSet.as_view(),
        name='users_detail'
    ),
]

urlpatterns = [
    path('v1/auth/', include(auth_endpoints)),
    path('v1/users/', include(users_endpoint)),
    path('v1/', include(v1_router.urls)),
]
