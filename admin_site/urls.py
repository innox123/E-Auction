
from django.urls import path
from .views import *

urlpatterns = [
    path('',main_admin, name="main-admin"),
    path('users/',user_admin,name="user-admin"),
    path('users/create/',create_user_admin,name="create-user-admin"),
    path('users/update/<int:user_id>/',update_user_admin,name="update-user-admin"),

    path('users/<int:pk>/delete/', delete_user, name='user-delete'),
    path('bid/<str:pk>/delete/', delete_bid, name='delete-bid'),

    # auction crud urls
    path('auctions/',get_auction_admin,name="auction-admin"),
    path('auctions/add/', add_auction_admin, name='add-auction'),
    path('auctions/<str:pk>/delete/', delete_auction, name='delete-auction'),

    # transaction admin urls
     path('transactions/',transaction_admin,name="transaction-admin"),
     path('approve/<uuid:transaction_id>',approve_payement,name="approve_payement"),

    # vehicle crud urls 
    path('vehicles/',get_vehicle_admin,name="vehicle-admin"),
    path('vehicles/auction/<str:auction_pk>/',all_vehicle_auction_admin,name="all-vehicle-auction"),
    path('vehicles/add/',add_vehicle_admin,name="add-vehicle"),
    path('vehicles/add/<str:auction_pk>/',add_vehicle_to_auction_admin,name="add-vehicle-auction"),
    path('vehicles/<str:pk>/update/', update_vehicle, name='update-vehicle'),
    path('vehicles/<str:pk>/delete/', delete_vehicle, name='delete-vehicle'),
    path('vehicles/auction/<str:pk>/delete/', remove_vehicle_auction, name='remove-vehicle-auction'),
    path('vehicles/<str:pk>/add-image/', add_vehicle_image, name='add-vehicle-image'),

    # authomated task urls
    path('automated_task/',automated_task_admin,name="automated-task-admin"),
    path('task/<str:name>/delete/', delete_periodic_tasks, name='delete-periodic-tasks'),
    path('result/<str:task_id>/delete/', delete_task_results, name='delete-task-results'),

    # car specifications urls 
    path('specifications/',specification_admin,name="specification-admin"),
    path('specifications/<str:spec_id>/update/', update_specifications_admin, name='update-specifications'),
    path('transactions/download/<uuid:transaction_id>/', download_bank_slip, name='download_bank_slip'),

]

