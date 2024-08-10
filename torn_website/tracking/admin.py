from django.contrib import admin

from .models import Faction, Member, Instance, Attack, Chain

admin.site.register((Faction, Member, Instance, Attack, Chain))
