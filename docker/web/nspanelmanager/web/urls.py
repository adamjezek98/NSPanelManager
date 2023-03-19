from django.contrib import admin
from django.urls import path, include

from . import views, api

urlpatterns = [
    # Web routes
    path('', views.index, name='index'),
    path('rooms', views.rooms, name='rooms'),
    path('rooms/order', views.rooms_order, name='rooms_order'),
    path('moveRoomUp/<int:room_id>', views.move_room_up, name='move_room_up'),
    path('moveRoomDown/<int:room_id>',
         views.move_room_down, name='move_room_down'),
    path('rooms/<int:room_id>/', views.edit_room, name='edit_room'),
    path('save_room/<int:room_id>',
         views.update_room_form, name='update_room_form'),
    path('remove_light/<int:room_id>/<int:light_id>',
         views.remove_light_from_room, name="remove_light_from_room"),
    path('add_light/<int:room_id>', views.add_light_to_room, name="add_new_light"),
    path('settings', views.settings_page, name="settings"),
    path('save_settings', views.save_settings, name="save_settings"),
    path('save_new_room', views.save_new_room, name='save_new_room'),
    path('save_new_firmware', views.save_new_firmware, name='save_new_firmware'),
    path('save_new_data_file', views.save_new_data_file, name='save_new_data_file'),
    path('save_new_tft_file', views.save_new_tft_file, name='save_new_tft_file'),
    path('download_firmware', views.download_firmware, name='download_firmware'),
    path('download_data_file', views.download_data_file, name='download_data_file'),
    path('download_tft', views.download_tft, name='download_tft'),
    path('checksum_firmware', views.checksum_firmware, name='checksum_firmware'),
    path('checksum_data_file', views.checksum_data_file, name='checksum_data_file'),
    # Below are API routes
    path('api/register_nspanel', api.register_nspanel, name='register_nspanel'),
    path('api/reboot_panel', api.reboot_nspanel, name='reboot_panel'),
    path('api/get_nspanel_config', api.get_nspanel_config,
         name='get_nspanel_config'),
    path('api/get_all_available_lights',
         api.get_all_available_light_entities, name='get_all_available_lights'),
    path('api/get_mqtt_manager_config', api.get_mqtt_manager_config,
         name='get_mqtt_manager_config')
]
