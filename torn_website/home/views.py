from datetime import timedelta
from random import choices
from string import ascii_letters, digits

from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone

from tracking.views import InstanceData, Faction


def random_id():
    return str().join(choices(ascii_letters + digits, k=20))


async def home(request):
    await Faction.delete_old_unused()
    if request.method == "GET":
        return render(request, "home/home.html")
    elif request.method == "POST":
        api_key = request.POST.get("api_key", None)

        if len(api_key) != 16:
            return HttpResponseBadRequest("Missing or invalid API key.")

        instance_data = InstanceData(api_key, random_id())
        try:
            await instance_data.update_or_create()
        except PermissionError:
            return render(request, status=400, template_name="400.html")
        if instance_data.faction.last_updated < timezone.now() - timedelta(minutes=1):
            print("This shouldnt run")
            await instance_data.request_data()
            return HttpResponseRedirect(f"/tracking/?id={instance_data.link_id}")
        else:
            return HttpResponseRedirect(f"/tracking/?id={instance_data.link_id}")
    else:
        return HttpResponseBadRequest()
