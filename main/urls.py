from django.urls import path
from . import views

urlpatterns = [
    # AUTH
    path('', views.login_view, name='login'),
    path('home/', views.home, name='home'),
    path('logout/', views.logout_view, name='logout'),

    # PAGES
    path('about-timergara-moqam/', views.team, name='about-timergara-moqam'),
    path('updates/', views.updates, name='updates'),

    # ELQA MAIN (IMPORTANT)
    path('elqa/<str:elqa_key>/', views.elqa_page, name='elqa_page'),

    # HALQA
    path('elqa/<str:elqa_key>/add-halqa/', views.add_halqa, name='add_halqa'),
    path('elqa/<str:elqa_key>/delete-halqa/<int:pk>/', views.delete_halqa, name='delete_halqa'),

    # MEMBER
    path('elqa/<str:elqa_key>/add-member/', views.add_member, name='add_member'),
    path('elqa/<str:elqa_key>/delete-member/<int:pk>/', views.delete_member, name='delete_member'),

    # UPDATE
    path('elqa/<str:elqa_key>/add-update/', views.add_update, name='add_update'),
    path('elqa/<str:elqa_key>/delete-update/<int:pk>/', views.delete_update, name='delete_update'),
    
    
    path('colleges/', views.colleges_home, name='colleges_home'),
    path('get-halqa-counts/', views.get_halqa_counts, name='get_halqa_counts'),
    
    
    path('elqa/<str:elqa_key>/add-member-ajax/', views.add_member_ajax, name='add_member_ajax'),

]





































































'''

from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('home', views.home, name='home'),
    path('about/', views.about, name='about'),

    # ❌ removed space URL (fixed)
    path('about-timergara-moqam/', views.team, name='team'),

    path('updates/', views.updates, name='updates'),

    # ELQA SECTION
    path('elqa/colleges/', views.elqa_colleges, name='elqa_collages'),

    path('elqa/sindhakhall/', views.elqa_sindhakhall, name='elqa_sindhakhall'),
    path('elqa/talash/', views.elqa_talash, name='elqa_talash'),
    path('elqa/collage/', views.elqa_collage, name='elqa_collage'),
    path('elqa/shaher/', views.elqa_shaher, name='elqa_shaher'),
    path('bazam/', views.elqa_bazam, name='bazam'),
    
    
    
    
    
    
    
    
    
    
    # Auth
   # path('login/',  views.login_view,  name='login'),
    path('logout/', views.logout_view, name='logout'),
    
     path('elqa/<str:elqa_key>/add-halqa/',           views.add_halqa,    name='add_halqa'),
    path('elqa/<str:elqa_key>/delete-halqa/<int:pk>/',views.delete_halqa,name='delete_halqa'),
    path('elqa/<str:elqa_key>/add-member/',          views.add_member,   name='add_member'),
    path('elqa/<str:elqa_key>/delete-member/<int:pk>/',views.delete_member,name='delete_member'),
    path('elqa/<str:elqa_key>/add-update/',          views.add_update,   name='add_update'),
    path('elqa/<str:elqa_key>/delete-update/<int:pk>/',views.delete_update,name='delete_update'),
]

'''