from django.db import models
from django.utils import timezone
from datetime import timedelta


class Faction(models.Model):
    @staticmethod
    async def delete_old_unused():
        one_day_ago = timezone.now() - timedelta(days=1)

        old_faction_objects = Faction.objects.filter(
            war_end__lt=one_day_ago.timestamp()
        )
        await old_faction_objects.adelete()

        unused_faction_objects = Faction.objects.filter(last_updated__lt=one_day_ago)
        await unused_faction_objects.adelete()

        ghost_attack_objects = Attack.objects.filter(factions__isnull=True)
        await ghost_attack_objects.adelete()

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20)
    war_id = models.IntegerField()
    war_start = models.IntegerField(blank=True, null=True)
    war_end = models.IntegerField(blank=True, null=True)
    last_known_attack = models.IntegerField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)


class Chain(models.Model):
    chain_id = models.IntegerField(primary_key=True)
    length = models.IntegerField(default=0)
    last_bonus = models.IntegerField(default=0)
    respect = models.FloatField(default=0)
    all_bonus_respect = models.FloatField(default=0)
    start = models.IntegerField(default=0)
    end = models.IntegerField(default=0)
    faction = models.ForeignKey(
        Faction, on_delete=models.CASCADE, related_name="chains"
    )


class Member(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20)
    faction = models.ForeignKey(
        Faction, on_delete=models.CASCADE, related_name="members"
    )
    war_hits = models.IntegerField(default=0)
    outside_chain_hits = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    score_war_attacks = models.FloatField(default=0)
    score_chain_attacks = models.FloatField(default=0)
    score_losses = models.FloatField(default=0)
    score_sum = models.FloatField(default=0)
    war_attack_pay = models.IntegerField(default=0)
    chain_attack_pay = models.IntegerField(default=0)
    loss_penalty = models.IntegerField(default=0)
    final_pay = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)


class Attack(models.Model):
    attack_id = models.IntegerField(primary_key=True)
    timestamp_started = models.IntegerField()
    timestamp_ended = models.IntegerField()
    attacker_id = models.IntegerField(blank=True, null=True)
    attacker_name = models.CharField(max_length=20, null=True)
    defender_id = models.IntegerField()
    defender_name = models.CharField(max_length=20)
    result = models.CharField(
        max_length=15,
        choices={
            "Arrested": "Arrested",
            "Assist": "Assist",
            "Attacked": "Attacked",
            "Escape": "Escape",
            "Hospitalized": "Hospitalized",
            "Interrupted": "Interrupted",
            "Looted": "Looted",
            "Mugged": "Mugged",
            "Special": "Special",
            "Stalemate": "Stalemate",
            "Timeout": "Timeout",
        },
    )
    respect = models.FloatField()
    chain_length = models.IntegerField()
    ranked_war = models.BooleanField()
    attacker_war_result = models.CharField(
        max_length=15, choices={"War": "War", "Chain": "Chain", "": ""}, default=""
    )
    defender_war_result = models.CharField(
        max_length=15, choices={"Loss": "Loss", "": ""}, default=""
    )
    chain = models.ForeignKey(
        Chain, on_delete=models.CASCADE, related_name="attacks", blank=True, null=True
    )
    factions = models.ManyToManyField(Faction, related_name="attacks")
    members = models.ManyToManyField(Member, related_name="attacks")


class Instance(models.Model):
    api_key = models.CharField(primary_key=True, max_length=64)
    link_id = models.URLField(max_length=42, unique=True)
    pay_per_hit = models.IntegerField(default=0)
    pay_per_outside_hit = models.IntegerField(default=0)
    penalty_per_loss = models.IntegerField(default=0)
    faction = models.ForeignKey(
        Faction, on_delete=models.CASCADE, related_name="instances", null=True
    )
