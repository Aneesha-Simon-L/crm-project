from django.urls import path

from.import views

urlpatterns = [
    path('dashboard/',views.DashBoardView.as_view(),name='dashboard'),
    path('students-list/',views.StudentsListView.as_view(),name='students-list'),
    path('form-list/',views.FormListView.as_view(),name='form-list'),
    path('student-detail/<str:uuid>/',views.StudentDetailView.as_view(),name='student-detail'),
    path('student-delete/<str:uuid>/',views.StudentDeleteView.as_view(),name='student-delete'),
    path('student-update/<str:uuid>/',views.StudentUpdateView.as_view(),name='student-update'),
    
    # path('course-list/',views.CourseListView.as_view(),name='course-list'),
    # path('batch-list/',views.BatchListView.as_view(),name='batch-list'),
]
