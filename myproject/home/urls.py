from django.contrib import admin
from django.urls import path, include
from home import views

urlpatterns = [
    path("", views.greet , name='greet'),
    path("contact-us", views.contactus , name='contactus'),
    path("mycontacts", views.mycontacts , name='mycontacts'),
    #admin urls
    path("admin_login", views.admin_login , name='admin_login'),
    path("admin_logout", views.admin_logout , name='admin_logout'),
    path("admin", views.admin , name='admin'),
    path("addnewproject", views.addnewproject , name='addnewproject'),
    path('delete/<int:id>/', views.delete , name='delete'),
    path('update/<int:id>/', views.update , name='update'),
    path('do_update/<int:id>/', views.do_update, name='do_update'),

    #explore urls
    path('explore', views.explore , name='explore'),
    # Gigs listing and API
    path('gigs/', views.gigs_list, name='gigs'),
    path('api/gigs/', views.gigs_api, name='gigs_api'),

    path('update_project/<int:id>/', views.update_project, name='update_project'),
    # admin delete route namespaced to avoid collision with user delete
    path('admin/my-projects/<int:id>/delete/', views.delete_project, name='delete_project'),
    path('ajax/add-skill/', views.ajax_add_skill, name='ajax_add_skill'),
    path('project/<int:id>/', views.project_detail, name='project_detail'),
    #user urls
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    #profile urls
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('my-projects/', views.user_projects, name='user_projects'),
    path('my-projects/add/', views.add_project, name='add_project'),
    path('my-projects/<int:id>/edit/', views.edit_project, name='edit_project'),
    path('my-projects/<int:id>/delete/', views.delete_project_user, name='delete_project_user'),
    path('profile/experience/add/', views.add_experience, name='add_experience'),
    path('profile/experience/<int:id>/edit/', views.edit_experience, name='edit_experience'),
    path('profile/experience/<int:id>/delete/', views.delete_experience, name='delete_experience'),
    path('profile/education/add/', views.add_education, name='add_education'),
    path('profile/education/<int:id>/edit/', views.edit_education, name='edit_education'),
    path('profile/education/<int:id>/delete/', views.delete_education, name='delete_education'),
    path('my-resume/', views.public_profile, name='public_profile'),
    path('user/<int:user_id>/', views.user_profile_view, name='user_profile'),
    path('users/', views.users_list, name='users'),
    # path('aboutus', views.about , name='greet')
]