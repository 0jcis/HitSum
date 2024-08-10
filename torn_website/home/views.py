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
        pay_p_hit = request.POST.get("war_hit", None)
        pay_p_outside_hit = request.POST.get("outside_hit", None)
        penalty_p_loss = request.POST.get("loss", None)

        if (
            not all((api_key, pay_p_hit, pay_p_outside_hit, penalty_p_loss))
            or len(api_key) != 16
        ):
            return HttpResponseBadRequest(
                "Missing or invalid required parameters. (api key, pay per war hit, pay per outside hit, pay per loss)"
            )
        for value in pay_p_hit, pay_p_outside_hit, penalty_p_loss:
            try:
                int(value)
            except ValueError:
                return HttpResponseBadRequest(
                    "Missing or invalid required parameters. (api key, pay per war hit, pay per outside hit, pay per loss)"
                )

        instance_data = InstanceData(
            api_key, pay_p_hit, pay_p_outside_hit, penalty_p_loss, random_id()
        )
        try:
            await instance_data.update_or_create()
        except PermissionError:
            return render(request, status=400, template_name="400.html")
        if instance_data.faction.last_updated < timezone.now() - timedelta(minutes=1):
            await instance_data.request_data()
            return HttpResponseRedirect(f"/tracking/?id={instance_data.link_id}")
        else:
            return HttpResponseRedirect(f"/tracking/?id={instance_data.link_id}")
