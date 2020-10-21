from django.urls import path
from apis import views

urlpatterns = [
    path('users/', views.UserList.as_view()),
    path('user/<int:pk>/', views.UserDetail.as_view()),
    path('current_user/', views.get_current_user),
    # path('workspaces/', views.WorkspaceList.as_view()),
    # path('workspace/<int:pk>/', views.WorkspaceDetail.as_view()),
    path('vias/', views.ViaList.as_view()),
    path('via/<int:pk>/', views.ViaDetail.as_view()),
    path('bms/', views.get_bm),
    path('ads_acc/', views.get_ads_acc),
    path('bms/<int:pk>/', views.BMDetail.as_view()),
]
