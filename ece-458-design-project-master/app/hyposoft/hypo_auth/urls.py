from django.urls import path
from . import views
from .views import ShibbolethView, ShibbolethLoginView
from . import generic_views


generic_views = [(name[:-4], cls) for name, cls in generic_views.__dict__.items() if isinstance(cls, type) and name[-4:] == "View"]
urlpatterns = []

for view in generic_views:
    url = view[0]
    obj = view[1].as_view()
    if url.endswith(('Retrieve', 'Update', 'Destroy')):
        url += '/<int:pk>'
    urlpatterns.append(
        path(url, obj)
    )

urlpatterns += [
    path('current_user', views.SessionView.as_view()),
    path('login', views.LoginView.as_view()),
    path('logout', views.LogoutView.as_view()),
    path('shib_login', ShibbolethLoginView.as_view()),
    path('shib_session', ShibbolethView.as_view()),
    path('UserCreate', views.UserCreate.as_view()),
    path('UserRetrieve/<int:pk>', views.UserRetrieve.as_view()),
    path('UserUpdate/<int:pk>', views.UserUpdate.as_view()),
    path('UserList', views.UserList.as_view()),
    path('UserDestroy/<int:pk>', views.UserDestroy.as_view())
]
