from celery import shared_task

from datetime import datetime

from .models import Instance, Faction, Chain, Member, Attack
from .views import InstanceData as InstanceDataView


class InstanceData(InstanceDataView):
    class AttackData(InstanceDataView.AttackData):
        def update_to_db(self, faction_object, member_object=None, chain_object=None):
            attack_object, attack_object_created = Attack.objects.update_or_create(
                attack_id=self.attack_id,
                defaults={
                    "timestamp_started": self.timestamp_started,
                    "timestamp_ended": self.timestamp_ended,
                    "attacker_id": self.attacker_id,
                    "attacker_name": self.attacker_name,
                    "defender_id": self.defender_id,
                    "defender_name": self.defender_name,
                    "result": self.result,
                    "respect": self.respect,
                    "chain_length": self.chain_length,
                    "group": self.group,
                    "ranked_war": self.ranked_war,
                    "attacker_war_result": self.attacker_war_result,
                    "defender_war_result": self.defender_war_result,
                },
            )
            if faction_object:
                attack_object.factions.add(faction_object)
            if member_object:
                attack_object.members.add(member_object)
            if chain_object:
                attack_object.chain = chain_object
            attack_object.save()
            return attack_object, attack_object_created

    class MemberData(InstanceDataView.MemberData):
        def update_to_db(self, faction_object):
            member_object, member_object_created = Member.objects.update_or_create(
                id=self.user_id,
                defaults={
                    "name": self.name,
                    "faction": faction_object,
                    "war_hits": self.war_hits,
                    "assists": self.assists,
                    "outside_chain_hits": self.outside_chain_hits,
                    "losses": self.losses,
                },
            )
            return member_object, member_object_created

    class ChainData(InstanceDataView.ChainData):
        def update_to_db(self, faction_object):
            chain_object, chain_object_created = Chain.objects.update_or_create(
                chain_id=self.chain_id,
                defaults={
                    "length": self.length,
                    "last_bonus": self.last_bonus,
                    "all_bonus_respect": self.all_bonus_respect,
                    "respect": self.respect,
                    "start": self.start,
                    "end": self.end,
                    "faction": faction_object,
                },
            )
            return chain_object, chain_object_created

    class FactionData(InstanceDataView.FactionData):
        def update_to_db(self):
            faction_object, faction_object_created = Faction.objects.update_or_create(
                id=self.faction_id,
                defaults={
                    "name": self.name,
                    "war_id": self.war_id,
                    "war_start": self.war_start,
                    "war_end": self.war_end,
                },
            )
            self.last_updated = faction_object.last_updated
            return faction_object, faction_object_created


def serialize_data(instance_data):

    def serialize_attack_data(attacks):
        ser_attacks = dict()
        for attack_id, attack_data in attacks.items():
            ser_attacks[attack_id] = {
                "attack_id": attack_data.attack_id,
                "timestamp_started": attack_data.timestamp_started,
                "timestamp_ended": attack_data.timestamp_ended,
                "attacker_id": attack_data.attacker_id,
                "attacker_name": attack_data.attacker_name,
                "defender_id": attack_data.defender_id,
                "defender_name": attack_data.defender_name,
                "result": attack_data.result,
                "respect": attack_data.respect,
                "chain_length": attack_data.chain_length,
                "group": attack_data.group,
                "ranked_war": attack_data.ranked_war,
                "attacker_war_result": attack_data.attacker_war_result,
                "defender_war_result": attack_data.defender_war_result,
            }
        return ser_attacks

    def serialize_member_data(members):
        ser_members = dict()
        for member_id, member_data in members.items():
            ser_members[member_id] = {
                "user_id": member_data.user_id,
                "name": member_data.name,
                "war_hits": member_data.war_hits,
                "assists": member_data.assists,
                "outside_chain_hits": member_data.outside_chain_hits,
                "losses": member_data.losses,
                "attacks": serialize_attack_data(member_data.attacks),
            }
        return ser_members

    def serialize_chain_data(chains):
        ser_chains = dict()
        for chain_id, chain_data in chains.items():
            ser_chains[chain_id] = {
                "chain_id": chain_data.chain_id,
                "length": chain_data.length,
                "last_bonus": chain_data.last_bonus,
                "respect": chain_data.respect,
                "all_bonus_respect": chain_data.all_bonus_respect,
                "start": chain_data.start,
                "end": chain_data.end,
                "attacks": serialize_attack_data(chain_data.attacks),
            }
        return ser_chains

    def serialize_faction_data(faction_data):
        ser_faction_data = {
            "faction_id": faction_data.faction_id,
            "name": faction_data.name,
            "war_id": faction_data.war_id,
            "war_start": faction_data.war_start,
            "war_end": faction_data.war_end,
            "members": serialize_member_data(faction_data.members),
            "attacks": serialize_attack_data(faction_data.attacks),
            "chains": serialize_chain_data(faction_data.chains),
            "last_updated": instance_data.faction.last_updated.timestamp(),
        }
        return ser_faction_data

    ser_instance_data = {
        "api_key": instance_data.api_key,
        "link_id": instance_data.link_id,
        "faction": serialize_faction_data(instance_data.faction),
    }

    return ser_instance_data


def unserialize_data(ser_instance_data):

    def unserialize_attack_data(ser_attacks):
        attacks = dict()
        for attack_id, ser_attack_data in ser_attacks.items():
            attacks[attack_id] = InstanceData.AttackData(
                attack_id=ser_attack_data["attack_id"],
                timestamp_started=ser_attack_data["timestamp_started"],
                timestamp_ended=ser_attack_data["timestamp_ended"],
                attacker_id=ser_attack_data["attacker_id"],
                attacker_name=ser_attack_data["attacker_name"],
                defender_id=ser_attack_data["defender_id"],
                defender_name=ser_attack_data["defender_name"],
                result=ser_attack_data["result"],
                respect=ser_attack_data["respect"],
                chain_length=ser_attack_data["chain_length"],
                group=ser_attack_data["group"],
                ranked_war=ser_attack_data["ranked_war"],
                attacker_war_result=ser_attack_data["attacker_war_result"],
                defender_war_result=ser_attack_data["defender_war_result"],
            )
        return attacks

    def unserialize_member_data(ser_members, attacks):
        members = dict()
        for member_id, ser_member_data in ser_members.items():
            members[member_id] = InstanceData.MemberData(
                user_id=ser_member_data["user_id"],
                name=ser_member_data["name"],
                war_hits=ser_member_data["war_hits"],
                assists=ser_member_data["assists"],
                outside_chain_hits=ser_member_data["outside_chain_hits"],
                losses=ser_member_data["losses"],
            )
            members[member_id].attacks = {
                attack_id: attacks[attack_id]
                for attack_id in ser_member_data["attacks"]
            }
        return members

    def unserialize_chain_data(ser_chains, attacks):
        chains = dict()
        for chain_id, ser_chain_data in ser_chains.items():
            chains[chain_id] = InstanceData.ChainData(
                chain_id=ser_chain_data["chain_id"],
                length=ser_chain_data["length"],
                respect=ser_chain_data["respect"],
                start=ser_chain_data["start"],
                end=ser_chain_data["end"],
            )
            chains[chain_id].attacks = {
                attack_id: attacks[attack_id] for attack_id in ser_chain_data["attacks"]
            }
        return chains

    def unserialize_faction_data(ser_faction_data):
        faction_data = InstanceData.FactionData(
            faction_id=ser_faction_data["faction_id"],
            name=ser_faction_data["name"],
            war_id=ser_faction_data["war_id"],
            war_start=ser_faction_data["war_start"],
            war_end=ser_faction_data["war_end"],
        )
        faction_data.attacks = unserialize_attack_data(ser_faction_data["attacks"])
        faction_data.members = unserialize_member_data(
            ser_faction_data["members"], faction_data.attacks
        )
        faction_data.chains = unserialize_chain_data(
            ser_faction_data["chains"], faction_data.attacks
        )
        faction_data.last_updated = datetime.fromtimestamp(
            ser_faction_data["last_updated"]
        )
        return faction_data

    instance_data = InstanceData(
        api_key=ser_instance_data["api_key"],
        link_id=ser_instance_data["link_id"],
        faction=unserialize_faction_data(ser_instance_data["faction"]),
    )
    return instance_data


@shared_task
def update_to_db(ser_instance_data):
    instance_data = unserialize_data(ser_instance_data)

    faction_object, faction_object_created = instance_data.faction.update_to_db()

    for chain_data in instance_data.faction.chains.values():
        chain_object, chain_object_created = chain_data.update_to_db(faction_object)
        for attack_data in chain_data.attacks.values():
            attack_data.update_to_db(
                faction_object=faction_object, chain_object=chain_object
            )

    for member_data in instance_data.faction.members.values():
        member_object, member_object_created = member_data.update_to_db(faction_object)
        for attack_data in member_data.attacks.values():
            attack_data.update_to_db(
                faction_object=faction_object, member_object=member_object
            )

    Instance.objects.update_or_create(
        api_key=instance_data.api_key,
        defaults={
            "link_id": instance_data.link_id,
            "faction": faction_object,
        },
    )


def update_to_db_in_background(instance_data):
    ser_instance_data = serialize_data(instance_data)
    update_to_db.delay(ser_instance_data)
