from django.urls import path
from apis import views

urlpatterns = [
    path("users/", views.UserList.as_view()),
    path("user/reset-password/<int:pk>/", views.UserResetPassword.as_view()),
    path("user/<int:pk>/", views.UserDetail.as_view()),
    path("current_user/", views.get_current_user),
    # path("workspaces/", views.WorkspaceList.as_view()),
    # path("workspace/<int:pk>/", views.WorkspaceDetail.as_view()),
    path("vias/", views.ViaList.as_view()),
    path("via/<int:pk>/", views.ViaDetail.as_view()),
    path("via-check-all/", views.CheckAllVias.as_view()),
    path("via-check/<int:pk>/", views.CheckVia.as_view()),
    path("bm-backup/", views.BackupBm.as_view()),
    path("bm-backup-all/", views.BackupAllBm.as_view()),
    path("bm-check/", views.CheckBm.as_view()),
    path("bm-check-all/", views.CheckAllBm.as_view()),
    path("bms/", views.BmList.as_view()),
    path("bms/ads_acc/", views.BmAdsAcc.as_view()),
    path("ads_acc/", views.AdsAccList.as_view()),
    path("bms/<int:pk>/", views.BmDetail.as_view()),
    path("logs/", views.LogList.as_view()),
    path("log/<int:pk>/", views.LogList.as_view()),
]
