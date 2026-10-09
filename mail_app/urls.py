from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
import os

urlpatterns = [
    path('', views.email_list, name='email_list'),
    path('email/<int:pk>/', views.email_detail, name='email_detail'),
    path('compose/', views.compose_email, name='compose_email'),
    path('trash/',views.trash_email,name='trash_email'),
    path('delete_email/<int:pk>/', views.delete_email, name='delete_email'),
    path('true_delete_email/<int:pk>/', views.true_delete_email,name='true_delete_email'),
    path('receive/', views.receive_email, name='receive_email'),
    path('contacts/',views.contacts,name='contacts'),
    path('restore_email/<int:pk>/', views.restore_email, name='restore_email'),
    path('trash/handle_actions/', views.handle_trash_actions, name='handle_trash_actions'),\
    path('unflag_email/<int:pk>/',views.unflag_email,name='unflag_email'),
    path('flagged_emails/',views.flagged_emails,name='flagged_emails'),
    path('flag_emal/<int:pk> ',views.flag_email,name='flag_email'),
    path('personal_info/', views.personal_info_view, name='personal_info'),
    path('personal_input/', views.personal_input_view, name='personal_input'),
    path('email/<int:pk>/download/<str:filename>/', views.download_attachment, name='download_attachment'),
    # path('drafts/', views.draft_list, name='drafts'),
    # path('drafts/delete/<int:draft_id>/', views.delete_draft, name='delete_draft'),
]

