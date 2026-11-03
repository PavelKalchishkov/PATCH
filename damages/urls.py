from django.urls import path

from damages import views

app_name = "damages"

urlpatterns = [
    path("map/", views.public_map, name="map"),
    path("map.geojson", views.map_geojson, name="map_geojson"),
    path("register/", views.public_register, name="register"),
    path("catalog/", views.catalog_list, name="catalog"),
    path("<uuid:detection_id>/priority/", views.override_priority, name="override_priority"),
]
