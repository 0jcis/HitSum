from datetime import datetime, timedelta
from time import sleep

from aiohttp import ClientSession
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.utils import timezone

from .models import Attack, Chain, Faction, Instance, Member


class InstanceData:
    class AttackData:
        def __init__(
            self,
            attack_id=None,
            timestamp_started=0,
            timestamp_ended=0,
            attacker_id=None,
            attacker_name="",
            defender_id=None,
            defender_name="",
            result="",
            respect=0.0,
            chain_length=0,
            group=False,
            ranked_war=None,
            attacker_war_result="",
            defender_war_result="",
        ):
            self.attack_id = attack_id
            self.timestamp_started = timestamp_started
            self.timestamp_ended = timestamp_ended
            self.attacker_id = attacker_id
            self.attacker_name = attacker_name
            self.defender_id = defender_id
            self.defender_name = defender_name
            self.result = result
            self.respect = respect
            self.chain_length = chain_length
            self.group = group
            self.ranked_war = ranked_war
            self.attacker_war_result = attacker_war_result
            self.defender_war_result = defender_war_result

        async def retrieve_from_db(self, attack_object):
            self.attack_id = attack_object.attack_id
            self.timestamp_started = attack_object.timestamp_started
            self.timestamp_ended = attack_object.timestamp_ended
            self.attacker_id = attack_object.attacker_id
            self.attacker_name = attack_object.attacker_name
            self.defender_id = attack_object.defender_id
            self.defender_name = attack_object.defender_name
            self.result = attack_object.result
            self.respect = attack_object.respect
            self.chain_length = attack_object.chain_length
            self.group = attack_object.group
            self.ranked_war = attack_object.ranked_war
            self.attacker_war_result = attack_object.attacker_war_result
            self.defender_war_result = attack_object.defender_war_result

        async def update_to_db(
            self, faction_object, member_object=None, chain_object=None
        ):
            attack_object, attack_object_created = (
                await Attack.objects.aupdate_or_create(
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
            )
            if faction_object:
                await sync_to_async(attack_object.factions.add)(faction_object)
            if member_object:
                await sync_to_async(attack_object.members.add)(member_object)
            if chain_object:
                attack_object.chain = chain_object
            await attack_object.asave()
            return attack_object, attack_object_created

    class MemberData:
        def __init__(
            self,
            user_id=None,
            name="",
            war_hits=0,
            assists=0,
            outside_chain_hits=0,
            losses=0,
        ):
            self.user_id = user_id
            self.name = name
            self.war_hits = war_hits
            self.assists = assists
            self.outside_chain_hits = outside_chain_hits
            self.losses = losses
            self.attacks = dict()

        async def retrieve_from_db(self, member_object):
            attack_objects = await sync_to_async(
                lambda: list(member_object.attacks.all())
            )()
            attacks = dict()
            for attack_object in attack_objects:
                attack_data = InstanceData.AttackData()
                await attack_data.retrieve_from_db(attack_object)
                attacks.update({attack_data.attack_id: attack_data})

            self.user_id = member_object.id
            self.name = member_object.name
            self.war_hits = member_object.war_hits
            self.assists = member_object.assists
            self.outside_chain_hits = member_object.outside_chain_hits
            self.losses = member_object.losses
            self.attacks = attacks

        async def update_to_db(self, faction_object):
            member_object, member_object_created = (
                await Member.objects.aupdate_or_create(
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
            )
            return member_object, member_object_created

    class ChainData:
        def __init__(
            self,
            chain_id=None,
            length=0,
            respect=0.0,
            start=None,
            end=None,
        ):
            self.chain_id = chain_id
            self.length = length
            self.last_bonus, self.all_bonus_respect = self.calculate_bonuses()
            self.respect = respect
            self.start = start
            self.end = end
            self.attacks = dict()

        def calculate_bonuses(self):
            chain_mech = dict()
            chain_mech["respect"] = {
                10: 10,
                25: 30,
                50: 70,
                100: 150,
                250: 310,
                500: 630,
                1000: 1270,
                2500: 2550,
                5000: 5110,
                10000: 10230,
                25000: 20470,
                50000: 40950,
                100000: 81910,
            }
            chain_mech["ranges"] = (
                (10, 25),
                (25, 50),
                (50, 100),
                (100, 250),
                (250, 500),
                (500, 1000),
                (1000, 2500),
                (2500, 5000),
                (5000, 10000),
                (10000, 25000),
                (25000, 50000),
                (50000, 100000),
            )

            for chain_range in chain_mech["ranges"]:
                if self.length in range(*chain_range):
                    max_chain = chain_range[0]
                    all_bonus_respect = chain_mech["respect"][max_chain]
                    return max_chain, all_bonus_respect
            return 100000, 81910

        async def retrieve_from_db(self, chain_object):
            attack_objects = await sync_to_async(
                lambda: list(chain_object.attacks.all())
            )()
            attacks = dict()
            for attack_object in attack_objects:
                attack_data = InstanceData.AttackData()
                await attack_data.retrieve_from_db(attack_object)
                attacks.update({attack_data.attack_id: attack_data})

            self.chain_id = chain_object.chain_id
            self.length = chain_object.length
            self.last_bonus = chain_object.last_bonus
            self.respect = chain_object.respect
            self.all_bonus_respect = chain_object.all_bonus_respect
            self.start = chain_object.start
            self.end = chain_object.end
            self.attacks = attacks

        async def update_to_db(self, faction_object):
            chain_object, chain_object_created = await Chain.objects.aupdate_or_create(
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

    class FactionData:
        def __init__(
            self, faction_id=None, name=None, war_id=None, war_start=None, war_end=None
        ):
            self.faction_id = faction_id
            self.name = name
            self.war_id = war_id
            self.war_start = war_start
            self.war_end = war_end
            self.members = dict()
            self.attacks = dict()
            self.chains = dict()
            self.last_updated = None

        async def retrieve_from_db(self, faction_object):
            chain_objects = await sync_to_async(
                lambda: list(faction_object.chains.all())
            )()
            chains = dict()
            for chain_object in chain_objects:
                chain_data = InstanceData.ChainData()
                await chain_data.retrieve_from_db(chain_object)
                chains.update({chain_data.chain_id: chain_data})

            member_objects = await sync_to_async(
                lambda: list(faction_object.members.all())
            )()
            members = dict()
            for member_object in member_objects:
                member_data = InstanceData.MemberData()
                await member_data.retrieve_from_db(member_object)
                members.update({member_data.user_id: member_data})

            attack_objects = await sync_to_async(
                lambda: list(faction_object.attacks.all())
            )()
            attacks = dict()
            for attack_object in attack_objects:
                attack_data = InstanceData.AttackData()
                await attack_data.retrieve_from_db(attack_object)
                attacks.update({attack_data.attack_id: attack_data})

            self.faction_id = faction_object.id
            self.name = faction_object.name
            self.war_id = faction_object.war_id
            self.war_start = faction_object.war_start
            self.war_end = faction_object.war_end
            self.chains = chains
            self.members = members
            self.attacks = attacks
            self.last_updated = faction_object.last_updated

        async def update_to_db(self):
            faction_object, faction_object_created = (
                await Faction.objects.aupdate_or_create(
                    id=self.faction_id,
                    defaults={
                        "name": self.name,
                        "war_id": self.war_id,
                        "war_start": self.war_start,
                        "war_end": self.war_end,
                    },
                )
            )
            self.last_updated = faction_object.last_updated
            return faction_object, faction_object_created

    def __init__(self, api_key=None, link_id=None, faction=FactionData()):
        self.api_key = api_key
        self.link_id = link_id
        self.faction = faction

    async def retrieve_from_db(self):
        instance_object = await Instance.objects.aget(link_id=self.link_id)

        faction_object = await sync_to_async(lambda: instance_object.faction)()

        self.api_key = instance_object.api_key
        self.faction = self.FactionData()

        await self.faction.retrieve_from_db(faction_object)

    async def update_or_create(self):
        instance_object, instance_object_created = (
            await Instance.objects.aupdate_or_create(
                api_key=self.api_key,
                defaults={
                    "link_id": self.link_id,
                },
            )
        )
        faction_object = await sync_to_async(lambda: instance_object.faction)()

        if instance_object_created or not faction_object:
            try:
                await self.request_data(save_now=True)
            except PermissionError:
                await instance_object.adelete()
                raise PermissionError(
                    "API key invalid, no permissions or torn API down."
                )

        else:
            self.faction = self.FactionData()
            await self.faction.retrieve_from_db(faction_object)

    async def request_data(self, save_now=False):
        # To prevent from getting triggered to update multiple times at once.
        if self.faction.faction_id:
            await self.faction.update_to_db()

        async def request_basic_data(session):
            params = {"key": self.api_key, "selections": "basic"}
            retries = 0
            response_successful = False

            while not response_successful:
                async with session.get("/faction", params=params) as resp:
                    resp.raise_for_status()
                    resp_basic_data = await resp.json()
                if "error" in resp_basic_data:
                    if resp_basic_data["error"]["code"] == 5:
                        sleep(60 - datetime.now().second)
                        retries += 1
                        raise RuntimeError("API overloaded.") if retries == 10 else None
                    else:
                        raise PermissionError(
                            "API key invalid, no permissions or torn API down."
                        )
                else:
                    response_successful = True

            self.faction.faction_id = resp_basic_data["ID"]
            self.faction.name = resp_basic_data["name"]
            self.faction.members = {
                int(user_id): InstanceData.MemberData(
                    user_id=int(user_id), name=data["name"]
                )
                for user_id, data in resp_basic_data["members"].items()
            }

        async def request_war_data(session):
            response_successful = False
            retries = 0
            params = {"key": self.api_key, "selections": "rankedwars"}

            while not response_successful:
                async with session.get("/faction", params=params) as resp:
                    resp.raise_for_status()
                    resp_war_data = await resp.json()

                if "error" in resp_war_data:
                    if resp_war_data["error"]["code"] == 5:
                        sleep(60 - datetime.now().second)
                        retries += 1
                        raise RuntimeError("API overloaded.") if retries == 10 else None
                    else:
                        raise PermissionError(
                            "API key invalid, no permissions or torn API down."
                        )
                else:
                    response_successful = True

            self.faction.war_id = str(
                max(int(war_id) for war_id in resp_war_data["rankedwars"].keys())
            )
            self.faction.war_start = resp_war_data["rankedwars"][self.faction.war_id][
                "war"
            ]["start"]
            self.faction.war_end = resp_war_data["rankedwars"][self.faction.war_id][
                "war"
            ]["end"]

        async def request_membership_data(session):
            membership_data = dict()
            retries = 0
            last_membership_response = None
            last_response_len = 100
            params = {
                "key": self.api_key,
                "selections": "membershipnews",
                "from": (
                    self.faction.war_end
                    if self.faction.war_end
                    else self.faction.war_start
                ),
            }

            while not last_response_len == 1:
                async with session.get("/faction", params=params) as resp:
                    resp.raise_for_status()
                    resp_membership_data = await resp.json()

                if "error" in resp_membership_data:
                    if resp_membership_data["error"]["code"] == 5:
                        sleep(60 - datetime.now().second)
                        retries += 1
                        raise RuntimeError("API overloaded.") if retries == 10 else None
                    raise PermissionError(
                        "API key invalid, no permissions or torn API down."
                    )
                else:
                    if (
                        last_membership_response
                        == resp_membership_data["membershipnews"]
                    ):
                        last_response_len = 1
                    else:
                        last_response_len = len(resp_membership_data["membershipnews"])
                    last_membership_response = resp_membership_data["membershipnews"]

                    if not last_membership_response:
                        break

                    membership_data.update(last_membership_response)

                    params["from"] = max(
                        int(membership["timestamp"])
                        for membership in last_membership_response.values()
                    )
            for membership in membership_data.values():
                leave_filter = ("left the faction", "was kicked out of the faction by")
                if any(identifier in membership["news"] for identifier in leave_filter):
                    split_1 = membership["news"].split(
                        "<a href = http://www.torn.com/profiles.php?XID="
                    )[1]
                    split_2 = split_1.split(">")
                    user_id = int(split_2[0])
                    name = split_2[1].split("</a")[0]

                    self.faction.members.update(
                        {user_id: InstanceData.MemberData(user_id=user_id, name=name)}
                    )

        async def request_attack_data(session):
            # Delete stored old attacks if new war started.
            attacks_before_war = dict(
                filter(
                    lambda x: x[1].timestamp_started < self.faction.war_start,
                    self.faction.attacks.items(),
                )
            )
            for attack in attacks_before_war:
                attack_object = await Attack.objects.aget(attack_id=attack)
                await attack_object.adelete()
                self.faction.attacks.pop(attack)

            attack_data = dict()
            last_attack_response = None
            last_response_len = 100
            retries = 0
            params = {
                "key": self.api_key,
                "selections": "attacks",
                "from": (
                    max(
                        attack.timestamp_started
                        for attack in self.faction.attacks.values()
                    )
                    if self.faction.attacks
                    else self.faction.war_start
                ),
                "to": self.faction.war_end,
            }
            while not last_response_len == 1:
                async with session.get("/faction", params=params) as resp:
                    resp.raise_for_status()
                    resp_attack_data = await resp.json()

                if "error" in resp_attack_data:
                    if resp_attack_data["error"]["code"] == 5:
                        sleep(60 - datetime.now().second)
                        retries += 1
                        raise RuntimeError("API overloaded.") if retries == 10 else None
                    else:
                        raise PermissionError(
                            "API key invalid, no permissions or torn API down."
                        )
                else:
                    if last_attack_response == resp_attack_data["attacks"]:
                        last_response_len = 1
                    else:
                        last_response_len = len(resp_attack_data["attacks"])
                    last_attack_response = resp_attack_data["attacks"]

                    if not last_attack_response:
                        break

                    attack_data.update(last_attack_response)
                    params["from"] = max(
                        int(attack["timestamp_started"])
                        for attack in last_attack_response.values()
                    )

            for attack_id, attack in attack_data.items():
                self.faction.attacks.update(
                    {
                        attack_id: InstanceData.AttackData(
                            attack_id=int(attack_id),
                            timestamp_started=int(attack["timestamp_started"]),
                            timestamp_ended=int(attack["timestamp_ended"]),
                            attacker_id=(
                                int(attack["attacker_id"])
                                if attack["attacker_id"]
                                else None
                            ),
                            attacker_name=attack["attacker_name"],
                            defender_id=int(attack["defender_id"]),
                            defender_name=attack["defender_name"],
                            result=attack["result"],
                            respect=attack["respect"],
                            chain_length=attack["chain"],
                            group=(
                                True
                                if attack["modifiers"]["group_attack"] > 1
                                else False
                            ),
                            ranked_war=bool(attack["ranked_war"]),
                        )
                    }
                )

        async def request_chain_data(session):
            # Delete stored old chains if new war started.
            chains_before_war = dict(
                filter(
                    lambda x: x[1].start < self.faction.war_start,
                    self.faction.chains.items(),
                )
            )
            for chain in chains_before_war:
                chain_object = await Chain.objects.aget(chain_id=chain)
                await chain_object.adelete()
                self.faction.chains.pop(chain)

            chain_data = dict()
            retries = 0
            last_chain_response = None
            last_response_len = 100
            params = {
                "key": self.api_key,
                "selections": "chains",
                "from": (
                    max(chain.end for chain in self.faction.chains.values())
                    if self.faction.chains
                    else self.faction.war_start
                ),
                "to": self.faction.war_end,
            }

            while not last_response_len == 1:
                async with session.get("/faction", params=params) as resp:
                    resp.raise_for_status()
                    resp_chain_data = await resp.json()

                if "error" in resp_chain_data:
                    if resp_chain_data["error"]["code"] == 5:
                        sleep(60 - datetime.now().second)
                        retries += 1
                        raise RuntimeError("API overloaded.") if retries == 10 else None
                    raise PermissionError(
                        "API key invalid, no permissions or torn API down."
                    )
                else:
                    if last_chain_response == resp_chain_data["chains"]:
                        last_response_len = 1
                    else:
                        last_response_len = len(resp_chain_data["chains"])
                    last_chain_response = resp_chain_data["chains"]

                    if not last_chain_response:
                        break

                    chain_data.update(last_chain_response)

                    params["from"] = max(
                        int(chain["start"]) for chain in last_chain_response.values()
                    )
            for chain_id, chain in chain_data.items():
                self.faction.chains.update(
                    {
                        chain_id: InstanceData.ChainData(
                            chain_id=chain_id,
                            length=chain["chain"],
                            respect=chain["respect"],
                            start=chain["start"],
                            end=chain["end"],
                        )
                    }
                )

        def assign_attacks():
            for member in self.faction.members.values():
                member.attacks = dict()

            for attack_id, attack in self.faction.attacks.items():
                if attack.attacker_id in self.faction.members:
                    self.faction.members[attack.attacker_id].attacks.update(
                        {attack_id: attack}
                    )
                elif attack.defender_id in self.faction.members:
                    self.faction.members[attack.defender_id].attacks.update(
                        {attack_id: attack}
                    )

        def count_losses():
            for member in self.faction.members.values():
                member.losses = 0

            for attack in self.faction.attacks.values():
                if all(
                    (
                        attack.defender_id in self.faction.members.keys(),
                        attack.ranked_war,
                        attack.result in ("Attacked", "Hospitalized", "Mugged"),
                    )
                ):
                    self.faction.members[attack.defender_id].losses += 1

                    attack.defender_war_result = "Loss"

        def count_chain_attacks():
            for member in self.faction.members.values():
                member.outside_chain_hits = 0

            for chain in self.faction.chains.values():
                for attack_id, attack in self.faction.attacks.items():
                    during_chain = attack.timestamp_ended in range(
                        chain.start, chain.end + 1
                    )
                    is_outside = not attack.ranked_war
                    is_chain = attack.chain_length in range(1, chain.last_bonus + 1)
                    is_member = (
                        attack.attacker_id in self.faction.members.keys()
                        if attack.attack_id
                        else False
                    )

                    if all((during_chain, is_outside, is_chain, is_member)):
                        member = self.faction.members[attack.attacker_id]
                        member.outside_chain_hits += 1

                        attack.attacker_war_result = "Chain"
                        chain.attacks.update({attack_id: attack})

        def count_assists():
            for member in self.faction.members.values():
                member.assists = 0

            for attack in self.faction.attacks.values():
                if (
                    attack.attacker_id in self.faction.members.keys()
                    and attack.result == "Assist"
                ):
                    attack_start = datetime.fromtimestamp(attack.timestamp_started)
                    group_attack_from = attack_start - timedelta(minutes=5)
                    group_attack_from = int(group_attack_from.timestamp())
                    group_attack_to = attack_start + timedelta(minutes=5)
                    group_attack_to = int(group_attack_to.timestamp())
                    for att in self.faction.attacks.values():
                        in_5_min = att.timestamp_started in range(
                            group_attack_from, group_attack_to
                        )
                        same_defender = att.defender_id == attack.defender_id

                        if all((in_5_min, att.group, same_defender)):
                            member = self.faction.members[attack.attacker_id]
                            member.assists += 1

                            attack.attacker_war_result = "Assist"

                            break

        def count_war_attacks():
            for member in self.faction.members.values():
                member.war_hits = 0

            for attack in self.faction.attacks.values():
                if all(
                    (
                        attack.attacker_id in self.faction.members.keys(),
                        attack.ranked_war,
                        attack.result in ("Attacked", "Hospitalized", "Mugged"),
                    )
                ):
                    member = self.faction.members[attack.attacker_id]
                    member.war_hits += 1

                    attack.attacker_war_result = "War"

        def remove_empty_members():
            empty_members = list()
            for user_id, member in self.faction.members.items():
                if all(
                    (
                        member.war_hits == 0,
                        member.assists == 0,
                        member.outside_chain_hits == 0,
                        member.losses == 0,
                    )
                ):
                    empty_members.append(user_id)
            for user_id in empty_members:
                self.faction.members.pop(user_id)

        async def update_to_db():
            faction_object, faction_object_created = await self.faction.update_to_db()
            for attack_data in self.faction.attacks.values():
                await attack_data.update_to_db(faction_object=faction_object)

            for chain_data in self.faction.chains.values():
                chain_object, chain_object_created = await chain_data.update_to_db(
                    faction_object
                )
                for attack_data in chain_data.attacks.values():
                    await attack_data.update_to_db(
                        faction_object=faction_object, chain_object=chain_object
                    )

            for member_data in self.faction.members.values():
                member_object, member_object_created = await member_data.update_to_db(
                    faction_object
                )
                for attack_data in member_data.attacks.values():
                    await attack_data.update_to_db(
                        faction_object=faction_object, member_object=member_object
                    )

            await Instance.objects.aupdate_or_create(
                api_key=self.api_key,
                defaults={
                    "link_id": self.link_id,
                    "faction": faction_object,
                },
            )

        async with ClientSession("https://api.torn.com") as client_session:
            await request_basic_data(client_session)
            await request_war_data(client_session)
            await request_membership_data(client_session)
            await request_attack_data(client_session)
            await request_chain_data(client_session)

        assign_attacks()
        count_war_attacks()
        count_assists()
        count_chain_attacks()
        count_losses()
        remove_empty_members()

        from .tasks import update_to_db_in_background

        (
            await update_to_db()
            if save_now
            else await sync_to_async(update_to_db_in_background)(self)
        )


async def tracking(request):
    if request.method == "GET":
        link_id = request.GET.get("id", None)
        if not link_id:
            return HttpResponseBadRequest("No id provided")

        instance_data = InstanceData(link_id=link_id)
        try:
            await instance_data.retrieve_from_db()
        except ObjectDoesNotExist:
            return render(request, "tracking/link_removed.html")

        if instance_data.faction.last_updated < timezone.now() - timedelta(minutes=1):
            await instance_data.request_data()

        faction = instance_data.faction
        chains = instance_data.faction.chains
        members = instance_data.faction.members

        for chain in chains.values():
            # noinspection PyTypeChecker
            start_human = datetime.fromtimestamp(chain.start).strftime(
                "%A, %d. %B %Y %I:%M%p"
            )
            # noinspection PyTypeChecker
            start_code = chain.start = datetime.fromtimestamp(chain.start).isoformat()

            # noinspection PyTypeChecker
            end_human = datetime.fromtimestamp(chain.end).strftime(
                "%A, %d. %B %Y %I:%M%p"
            )
            # noinspection PyTypeChecker
            end_code = datetime.fromtimestamp(chain.end).isoformat()

            chain.start = start_human, start_code
            chain.end = end_human, end_code

        for member in members.values():
            for attack_id, attack in member.attacks.items():
                # noinspection PyTypeChecker
                start_human = datetime.fromtimestamp(attack.timestamp_started).strftime(
                    "%d/%m/%y %I:%M%p"
                )
                # noinspection PyTypeChecker
                start_code = attack.timestamp_started = datetime.fromtimestamp(
                    attack.timestamp_started
                ).isoformat()

                # noinspection PyTypeChecker
                end_human = datetime.fromtimestamp(attack.timestamp_ended).strftime(
                    "%d/%m/%y %I:%M%p"
                )
                # noinspection PyTypeChecker
                end_code = datetime.fromtimestamp(attack.timestamp_ended).isoformat()

                attack.timestamp_started = start_human, start_code
                attack.timestamp_started = start_human, start_code
                attack.timestamp_ended = end_human, end_code
        return render(
            request,
            "tracking/tracking.html",
            context={
                "members": members,
                "chains": chains,
                "faction": faction,
                "instance": instance_data,
            },
        )
