from django.urls import path
from .views import BookPostView, ScenarioScriptView, PresenterPackageFormView, FileView

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
    path('book/<str:book_number>/<str:user_cave>/<int:scenario>/', BookPostView.as_view()),
    path('script/<str:book_number>/<str:user_cave>/<int:scenario>/', ScenarioScriptView.as_view()),
    path('form/', PresenterPackageFormView.as_view()),
    path('upload/<str:book_number>/<str:user_cave>/<int:scenario>/', FileView.as_view(), name='file-upload'),
]