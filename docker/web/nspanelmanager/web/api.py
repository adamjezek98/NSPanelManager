from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
import json
import requests

import hashlib
import psutil
import subprocess

from .models import NSPanel, Room, Light
from web.settings_helper import get_setting_with_default


def restart_mqtt_manager():
    for proc in psutil.process_iter():
        if "./mqtt_manager.py" in proc.cmdline():
            print("Killing existing mqtt_manager")
            proc.kill()
    # Restart the process
    print("Starting a new mqtt_manager")
    subprocess.Popen(
        ["/usr/local/bin/python", "./mqtt_manager.py"], cwd="/usr/src/app/")


def get_mqtt_manager_config(request):
    return_json = {}
    return_json["color_temp_min"] = int(
        get_setting_with_default("color_temp_min", 2000))
    return_json["color_temp_max"] = int(
        get_setting_with_default("color_temp_max", 6000))
    return_json["mqtt_server"] = get_setting_with_default("mqtt_server", "")
    return_json["mqtt_port"] = int(get_setting_with_default("mqtt_port", 1883))
    return_json["mqtt_username"] = get_setting_with_default(
        "mqtt_username", "")
    return_json["mqtt_password"] = get_setting_with_default(
        "mqtt_password", "")
    return_json["home_assistant_address"] = get_setting_with_default(
        "home_assistant_address", "")
    return_json["home_assistant_token"] = get_setting_with_default(
        "home_assistant_token", "")
    return_json["openhab_address"] = get_setting_with_default(
        "openhab_address", "")
    return_json["openhab_token"] = get_setting_with_default(
        "openhab_token", "")
    return_json["openhab_brightness_channel_name"] = get_setting_with_default(
        "openhab_brightness_channel_name", "")
    return_json["openhab_brightness_channel_min"] = get_setting_with_default(
        "openhab_brightness_channel_min", 0)
    return_json["openhab_brightness_channel_max"] = get_setting_with_default(
        "openhab_brightness_channel_max", 255)
    return_json["openhab_color_temp_channel_name"] = get_setting_with_default(
        "openhab_color_temp_channel_name", "")
    return_json["openhab_rgb_channel_name"] = get_setting_with_default(
        "openhab_rgb_channel_name", "")

    return_json["lights"] = {}
    for light in Light.objects.all():
        lightConfig = {}
        lightConfig["id"] = light.id
        lightConfig["name"] = light.friendly_name
        lightConfig["type"] = light.type
        lightConfig["can_dim"] = light.can_dim
        lightConfig["can_color_temperature"] = light.can_color_temperature
        lightConfig["can_rgb"] = light.can_rgb
        lightConfig["home_assistant_name"] = light.home_assistant_name
        lightConfig["openhab_name"] = light.openhab_name
        lightConfig["openhab_control_mode"] = light.openhab_control_mode
        lightConfig["openhab_item_switch"] = light.openhab_item_switch
        lightConfig["openhab_item_dimmer"] = light.openhab_item_dimmer
        lightConfig["openhab_item_color_temp"] = light.openhab_item_color_temp
        lightConfig["openhab_item_rgb"] = light.openhab_item_rgb
        return_json["lights"][light.id] = lightConfig

    return_json["nspanels"] = {}
    for panel in NSPanel.objects.all():
        panel_config = {
            "id": panel.id,
            "mac": panel.mac_address,
            "name": panel.friendly_name
        }
        return_json["nspanels"][panel.id] = panel_config

    return JsonResponse(return_json)


def get_all_available_light_entities(request):
    # TODO: Implement manually entered entities
    # Get Home Assistant lights
    return_json = {}
    return_json["home_assistant_lights"] = []
    return_json["openhab_lights"] = []
    return_json["manual_lights"] = []

    # Home Assistant
    if get_setting_with_default("home_assistant_token", "") != "":
        home_assistant_request_headers = {
            "Authorization": "Bearer " + get_setting_with_default("home_assistant_token", ""),
            "content-type": "application/json",
        }
        try:
            home_assistant_response = requests.get(
                get_setting_with_default("home_assistant_address", "") + "/api/states", headers=home_assistant_request_headers, timeout=5)
            for entity in home_assistant_response.json():
                if (entity["entity_id"].startswith("light.")):
                    return_json["home_assistant_lights"].append({
                        "label": entity["entity_id"].replace("light.", ""),
                        "items": []
                    })
        except:
            print("Failed to get Home Assistant lights!")

    # OpenHAB
    if get_setting_with_default("openhab_token", "") != "":
        # TODO: Sort out how to map channels from items to the correct POST request when MQTT is received
        openhab_request_headers = {
            "Authorization": "Bearer " + get_setting_with_default("openhab_token", ""),
            "content-type": "application/json",
        }
        openhab_response = requests.get(get_setting_with_default(
            "openhab_address", "") + "/rest/things", headers=openhab_request_headers)

        for entity in openhab_response.json():
            if "channels" in entity:
                add_entity = False
                items = []
                for channel in entity["channels"]:
                    # Check if this thing has a channel that indicates that it might be a light
                    if "itemType" in channel and (channel["itemType"] == "Dimmer" or channel["itemType"] == "Number" or channel["itemType"] == "Color" or channel["itemType"] == "Switch"):
                        add_entity = True
                    if "linkedItems" in channel:
                        # Add all available items to the list of items for this thing
                        for linkedItem in channel["linkedItems"]:
                            if linkedItem not in items:
                                items.append(linkedItem)
                if add_entity:
                    # return_json["openhab_lights"].append(entity["label"])
                    return_json["openhab_lights"].append({
                        "label": entity["label"],
                        "items": items
                    })

    return JsonResponse(return_json)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@csrf_exempt
def register_nspanel(request):
    """Update the already existing NSPanel OR create a new one"""
    data = json.loads(request.body)
    new_panel = NSPanel.objects.filter(mac_address=data['mac_address']).first()

    if not new_panel:
        new_panel = NSPanel()

    new_panel.friendly_name = data['friendly_name']
    new_panel.mac_address = data['mac_address']
    new_panel.version = data["version"]
    new_panel.last_seen = datetime.now()
    new_panel.ip_address = get_client_ip(request)

    # If no room is set, select the first one as default
    try:
        if not new_panel.room:
            new_panel.room = Room.objects.first()
    except NSPanel.room.RelatedObjectDoesNotExist:
        new_panel.room = Room.objects.first()

    # Save the update/Create new panel
    new_panel.save()
    restart_mqtt_manager()
    return HttpResponse('OK', status=200)


def delete_panel(request, panel_id: int):
    NSPanel.objects.get(id=panel_id).delete()
    return redirect('/')


def get_nspanel_config(request):
    nspanel = NSPanel.objects.get(mac_address=request.GET["mac"])
    base = {}
    base["home"] = nspanel.room.id
    base["raise_to_100_light_level"] = get_setting_with_default(
        "raise_to_100_light_level", 95)
    base["color_temp_min"] = get_setting_with_default("color_temp_min", 2000)
    base["color_temp_max"] = get_setting_with_default("color_temp_max", 6000)
    base["reverse_color_temp"] = get_setting_with_default("reverse_color_temp", False)
    base["min_button_push_time"] = get_setting_with_default("min_button_push_time", 50)
    base["button_long_press_time"] = get_setting_with_default("button_long_press_time", 5000)
    base["special_mode_trigger_time"] = get_setting_with_default("special_mode_trigger_time", 300)
    base["special_mode_release_time"] = get_setting_with_default("special_mode_release_time", 5000)
    base["mqtt_ignore_time"] = get_setting_with_default("mqtt_ignore_time", 3000)
    base["button1_mode"] = nspanel.button1_mode
    if nspanel.button1_detached_mode_light:
        base["button1_detached_light"] = nspanel.button1_detached_mode_light.id
    else:
        base["button1_detached_mode_light"] = -1
    base["button2_mode"] = nspanel.button2_mode
    if nspanel.button2_detached_mode_light:
        base["button2_detached_light"] = nspanel.button2_detached_mode_light.id
    else:
        base["button2_detached_light"] = -1
    base["rooms"] = []
    for room in Room.objects.all().order_by('displayOrder'):
        base["rooms"].append(room.id)
    return JsonResponse(base)


def get_room_config(request, room_id: int):
    room = Room.objects.get(id=room_id)
    return_json = {}
    return_json["name"] = room.friendly_name
    return_json["lights"] = {}
    for light in room.light_set.all():
        return_json["lights"][light.id] = {}
        return_json["lights"][light.id]["name"] = light.friendly_name
        return_json["lights"][light.id]["ceiling"] = light.is_ceiling_light
        return_json["lights"][light.id]["can_dim"] = light.can_dim
        return_json["lights"][light.id]["can_temperature"] = light.can_color_temperature
        return_json["lights"][light.id]["can_rgb"] = light.can_rgb
        return_json["lights"][light.id]["view_position"] = light.room_view_position
    return JsonResponse(return_json)


def get_light_config(request, light_id: int):
    light = Light.objects.get(id=light_id)
    return_json = {}
    return_json["id"] = light.id
    return_json["name"] = light.friendly_name
    return_json["type"] = light.type
    return_json["ceiling"] = light.is_ceiling_light
    return_json["can_dim"] = light.can_dim
    return_json["can_color_temperature"] = light.can_color_temperature
    return_json["can_rgb"] = light.can_rgb
    return_json["home_assistant_name"] = light.home_assistant_name
    return_json["openhab_name"] = light.openhab_name
    return_json["openhab_control_mode"] = light.openhab_control_mode
    return_json["openhab_item_switch"] = light.openhab_item_switch
    return_json["openhab_item_dimmer"] = light.openhab_item_dimmer
    return_json["openhab_item_color_temp"] = light.openhab_item_color_temp
    return_json["openhab_item_rgb"] = light.openhab_item_rgb
    return JsonResponse(return_json)


def reboot_nspanel(request):
    address = request.GET["address"]
    try:
        requests.get(F"http://{address}/do_reboot")
    except:
        pass
    return redirect("/")


@csrf_exempt
def set_panel_status(request, panel_mac: str):
    nspanels = NSPanel.objects.filter(mac_address=panel_mac)
    if nspanels.exists():
        nspanel = nspanels.first()
        # We got a match
        json_payload = json.loads(request.body.decode('utf-8'))
        nspanel.wifi_rssi = int(json_payload["rssi"])
        nspanel.heap_used_pct = int(json_payload["heap_used_pct"])
        nspanel.save()
        return HttpResponse("", status=200)

    return HttpResponse("", status=500)


@csrf_exempt
def set_panel_online_status(request, panel_mac: str):
    nspanels = NSPanel.objects.filter(mac_address=panel_mac)
    if nspanels.exists():
        nspanel = nspanels.first()
        # We got a match
        payload = json.loads(request.body.decode('utf-8'))
        nspanel.online_state = (payload["state"] == "online")
        nspanel.save()
        return HttpResponse("", status=200)

    return HttpResponse("Panel is not registered", status=500)
