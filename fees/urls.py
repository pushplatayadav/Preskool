from django.urls import path
from . import views

app_name = "fees"

urlpatterns = [
    path("student-fees/<int:pk>/", views.student_fees, name="student-fees"),
    path("collect-fees/", views.collect_fees, name="collect-fees"),
    path("fees-group/", views.fees_group_list, name="fees-group-list"),
    path("fees-group/<int:pk>/edit/", views.fees_group_edit, name="fees-group-edit"),
    path("fees-group/<int:pk>/delete/", views.fees_group_delete, name="fees-group-delete"),
    path("fees-type/", views.fees_type_list, name="fees-type-list"),
    path("fees-type/<int:pk>/edit/", views.fees_type_edit, name="fees-type-edit"),
    path("fees-type/<int:pk>/delete/", views.fees_type_delete, name="fees-type-delete"),
    path("fees-master/", views.fees_master_list, name="fees-master-list"),
    path("fees-master/<int:pk>/edit/", views.fees_master_edit, name="fees-master-edit"),
    path("fees-master/<int:pk>/delete/", views.fees_master_delete, name="fees-master-delete"),
    path("fees-assign/", views.fees_assign_list, name="fees-assign-list"),
    path("fees-assign/search/", views.fees_assign_search, name="fees-assign-search"),
    path("fees-assign/<int:pk>/edit/", views.fees_assign_edit, name="fees-assign-edit"),
    path("fees-assign/<int:pk>/delete/", views.fees_assign_delete, name="fees-assign-delete"),
]
