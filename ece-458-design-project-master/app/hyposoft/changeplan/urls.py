from django.urls import path
from .views import ChangePlanList, ChangePlanDetails, ChangePlanCreate, ChangePlanDestroy, ChangePlanUpdate, \
    ChangePlanActions, ExecuteChangePlan

urlpatterns = [
    path('ChangePlanList', ChangePlanList.as_view()),
    path('ChangePlanDetails/<int:pk>', ChangePlanDetails.as_view()),
    path('ChangePlanCreate', ChangePlanCreate.as_view()),
    path('ChangePlanDestroy/<int:pk>', ChangePlanDestroy.as_view()),
    path('ChangePlanUpdate/<int:pk>', ChangePlanUpdate.as_view()),
    path('ChangePlanActions/<int:pk>', ChangePlanActions.as_view()),
    path('ChangePlanExecute/<int:pk>', ExecuteChangePlan.as_view())
]
