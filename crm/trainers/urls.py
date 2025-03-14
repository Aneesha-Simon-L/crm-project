from django.urls import path

from.import views

urlpatterns = [
    path('trainers-list/',views.TrainerListView.as_view(),name='trainers-list'),
    path('trainer-form/',views.TrainerFormView.as_view(),name='trainer-form'),
    path('trainer-detail/<str:uuid>/',views.TrainerDetailView.as_view(),name='trainer-detail'),
    path('trainer-delete/<str:uuid>/',views.TrainerDeleteView.as_view(),name='trainer-delete'),
    path('trainer-update/<str:uuid>/',views.TrainerUpdateView.as_view(),name='trainer-update'),
]
