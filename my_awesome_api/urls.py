from django.urls import include, path
from rest_framework import routers
from .views import BookPostView

'''
router = routers.DefaultRouter()
router.register(r'book', views.BookPostView, basename='Book')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
'''

app_name = "book"

# app_name will help us do a reverse look-up latter.
urlpatterns = [
    path('book/<int:book_number>/<int:scenario>/<str:username>/', BookPostView.as_view()),
]