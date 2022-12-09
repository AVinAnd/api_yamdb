from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import TokenSerializer
from .views import (signup, UsersViewSet, CategoryViewSet, CommentViewSet,
                    GenreViewSet, ReviewViewSet, TitleViewSet)

app_name = 'api'

users_router_v1 = DefaultRouter()
users_router_v1.register(r'', UsersViewSet)
users_router_v1.register(r'^[\w.@+-]+\Z', UsersViewSet)

router_v1 = DefaultRouter()
router_v1.register('categories', CategoryViewSet)
router_v1.register('genres', GenreViewSet)
router_v1.register('titles', TitleViewSet)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='review'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comment'
)

urlpatterns = [
    path('v1/auth/signup/', signup),
    path('v1/users/', include(users_router_v1.urls)),
    path(
        'v1/auth/token/',
        TokenObtainPairView.as_view(serializer_class=TokenSerializer),
        name='token'
    ),
    path('v1/', include(router_v1.urls))
]
