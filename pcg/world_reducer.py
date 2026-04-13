import json
import random
from typing import Dict, Any, List, Optional, Tuple, Set
from .world_state import WorldState

class WorldReducer:
    def __init__(self, world_state: WorldState):
        self.ws = world_state

    # ---- Helper methods ----
    def _get_negative_relations(self, entity_type: str, entity_name: str) -> List[Tuple[str, str]]:
        """Return list of (target_type, target_name) for relations with negative favorability."""
        result = []
        if entity_type == "npc":
            data = self.ws.npcs.get(entity_name, {})
            for rel in data.get("Relations", []):
                if rel.get("Favorability", 0) < 0:
                    target = rel["Target"]
                    if target in self.ws.npcs:
                        result.append(("npc", target))
                    elif target in self.ws.factions:
                        result.append(("faction", target))
        elif entity_type == "faction":
            data = self.ws.factions.get(entity_name, {})
            for rel in data.get("Relations", []):
                if rel.get("Favorability", 0) < 0:
                    target = rel["Target"]
                    if target in self.ws.npcs:
                        result.append(("npc", target))
                    elif target in self.ws.factions:
                        result.append(("faction", target))
        return result

    def _get_random_member(self, faction_name: str) -> Optional[str]:
        members = self.ws.factions.get(faction_name, {}).get("Members", [])
        if members:
            return random.choice(members)
        return None

    def _filter_relations(self, relations: List[Dict], allowed_targets: Set[str]) -> List[Dict]:
        """Return a copy of relations where Target is in allowed_targets."""
        return [r for r in relations if r.get("Target") in allowed_targets]

    def _simplify_npc(self, npc_name: str, allowed_targets: Set[str]) -> Dict[str, Any]:
        npc = self.ws.npcs.get(npc_name, {})
        relations = npc.get("Relations", [])
        filtered_relations = self._filter_relations(relations, allowed_targets)
        return {
            "Name": npc.get("Name", npc_name),
            "Species": npc.get("Species", ""),
            "Role": npc.get("Role", ""),
            "CurrentLocation": npc.get("CurrentLocation", ""),
            "HomeLocation": npc.get("HomeLocation", ""),
            "OwnedItems": npc.get("OwnedItems", {}),
            "Faction": npc.get("Faction", ""),
            "Relations": filtered_relations
        }

    def _simplify_faction(self, faction_name: str, allowed_targets: Set[str], keep_members: bool = False) -> Dict[str, Any]:
        faction = self.ws.factions.get(faction_name, {})
        relations = faction.get("Relations", [])
        filtered_relations = self._filter_relations(relations, allowed_targets)
        # Accept both "DefaultLocation" (camelCase) and "Default_Location" (snake_case)
        default_loc = faction.get("DefaultLocation") or faction.get("Default_Location", "")
        simplified = {
            "Name": faction.get("Name", faction_name),
            "Relations": filtered_relations,
            "Default_Location": default_loc
        }
        if keep_members:
            simplified["Members"] = faction.get("Members", [])
        return simplified

    def _simplify_location(self, location_name: str) -> Dict[str, Any]:
        loc = self.ws.locations.get(location_name, {})
        return {
            "Name": loc.get("Name", location_name),
            "Enemies": loc.get("Enemies", []),
            "Resources": loc.get("Resources", [])
        }

    # ---- Reduction strategies ----
    def reduce_around_faction(self, faction_name: str) -> Dict[str, Any]:
        """
        Focus: a faction.
        Output includes:
        - the focus faction
        - one enemy faction (negative relation)
        - one member NPC from the focus faction
        - one enemy NPC from the enemy faction
        """
        enemies = self._get_negative_relations("faction", faction_name)
        enemy_factions = [t for t in enemies if t[0] == "faction"]
        if not enemy_factions:
            print(f"Warning: No enemy factions found for {faction_name}. Falling back to random faction.")
            other_factions = [f for f in self.ws.factions if f != faction_name]
            if other_factions:
                enemy_faction_name = random.choice(other_factions)
            else:
                return {}
        else:
            enemy_faction_name = random.choice(enemy_factions)[1]

        focus_member = self._get_random_member(faction_name)
        if not focus_member:
            print(f"Warning: No members in focus faction {faction_name}. Cannot generate.")
            return {}

        enemy_members = self.ws.factions.get(enemy_faction_name, {}).get("Members", [])
        if not enemy_members:
            print(f"Warning: Enemy faction {enemy_faction_name} has no members. Cannot generate.")
            return {}
        enemy_npc = random.choice(enemy_members)

        result = {}

        allowed_entities = {faction_name, enemy_faction_name, focus_member, enemy_npc, self.ws.player_name}
        allowed_entities.add(self.ws.player_name)

        result["Factions"] = {
            faction_name: self._simplify_faction(faction_name, allowed_entities, keep_members=False),
            enemy_faction_name: self._simplify_faction(enemy_faction_name, allowed_entities, keep_members=False)
        }

        result["NPCs"] = {
            focus_member: self._simplify_npc(focus_member, allowed_entities),
            enemy_npc: self._simplify_npc(enemy_npc, allowed_entities)
        }

        # Collect locations
        locs = set()
        for npc in [focus_member, enemy_npc]:
            data = self.ws.npcs.get(npc, {})
            if data.get("CurrentLocation"):
                locs.add(data["CurrentLocation"])
            if data.get("HomeLocation"):
                locs.add(data["HomeLocation"])
        for faction in [faction_name, enemy_faction_name]:
            fac_data = self.ws.factions.get(faction, {})
            default_loc = fac_data.get("DefaultLocation") or fac_data.get("Default_Location")
            if default_loc:
                locs.add(default_loc)

        if locs:
            result["Locations"] = {}
            for loc in locs:
                loc_data = self.ws.locations.get(loc)
                if loc_data:
                    result["Locations"][loc] = self._simplify_location(loc)

        # Player relations
        player = self.ws.player.copy()
        faction_rels = player.get("FactionRelations", [])
        filtered_faction_rels = [r for r in faction_rels if r.get("Target") in allowed_entities]
        player["FactionRelations"] = filtered_faction_rels
        npc_rels = player.get("NPCRelations", [])
        filtered_npc_rels = [r for r in npc_rels if r.get("Target") in allowed_entities]
        player["NPCRelations"] = filtered_npc_rels
        if filtered_faction_rels or filtered_npc_rels:
            result["Player"] = player

        return result

    def reduce_around_npc(self, npc_name: str) -> Dict[str, Any]:
        """
        Focus: an NPC.
        Output includes:
        - the focus NPC
        - its faction
        - one disliked NPC (negative relation)
        - the disliked NPC's faction
        If no disliked NPC, fallback to a disliked faction (or focus's faction's enemy),
        then pick an NPC from that enemy faction.
        """
        npc = self.ws.npcs.get(npc_name)
        if not npc:
            return {}

        focus_faction = npc.get("Faction")

        disliked = self._get_negative_relations("npc", npc_name)
        disliked_npcs = [t for t in disliked if t[0] == "npc"]
        disliked_npc_name = None
        enemy_faction_name = None

        if disliked_npcs:
            disliked_npc_name = random.choice(disliked_npcs)[1]
            enemy_npc_data = self.ws.npcs.get(disliked_npc_name, {})
            enemy_faction_name = enemy_npc_data.get("Faction")
        else:
            disliked_factions = [t for t in disliked if t[0] == "faction"]
            if disliked_factions:
                enemy_faction_name = random.choice(disliked_factions)[1]
            elif focus_faction:
                faction_enemies = self._get_negative_relations("faction", focus_faction)
                faction_enemy_factions = [t for t in faction_enemies if t[0] == "faction"]
                if faction_enemy_factions:
                    enemy_faction_name = random.choice(faction_enemy_factions)[1]
            if enemy_faction_name:
                members = self.ws.factions.get(enemy_faction_name, {}).get("Members", [])
                if members:
                    disliked_npc_name = random.choice(members)
                else:
                    print(f"Warning: Enemy faction {enemy_faction_name} has no members. Cannot generate.")
                    return {}
            else:
                print(f"Warning: No disliked NPC or faction found for {npc_name}. Cannot generate.")
                return {}

        result = {}

        allowed_entities = {npc_name, disliked_npc_name, self.ws.player_name}
        if focus_faction:
            allowed_entities.add(focus_faction)
        if enemy_faction_name:
            allowed_entities.add(enemy_faction_name)

        result["NPCs"] = {
            npc_name: self._simplify_npc(npc_name, allowed_entities),
            disliked_npc_name: self._simplify_npc(disliked_npc_name, allowed_entities)
        }

        result["Factions"] = {}
        if focus_faction:
            result["Factions"][focus_faction] = self._simplify_faction(focus_faction, allowed_entities, keep_members=False)
        if enemy_faction_name:
            result["Factions"][enemy_faction_name] = self._simplify_faction(enemy_faction_name, allowed_entities, keep_members=False)

        # Collect locations
        locs = set()
        for npc in [npc_name, disliked_npc_name]:
            data = self.ws.npcs.get(npc, {})
            if data.get("CurrentLocation"):
                locs.add(data["CurrentLocation"])
            if data.get("HomeLocation"):
                locs.add(data["HomeLocation"])
        if focus_faction:
            fac_data = self.ws.factions.get(focus_faction, {})
            default_loc = fac_data.get("DefaultLocation") or fac_data.get("Default_Location")
            if default_loc:
                locs.add(default_loc)
        if enemy_faction_name:
            fac_data = self.ws.factions.get(enemy_faction_name, {})
            default_loc = fac_data.get("DefaultLocation") or fac_data.get("Default_Location")
            if default_loc:
                locs.add(default_loc)

        if locs:
            result["Locations"] = {}
            for loc in locs:
                loc_data = self.ws.locations.get(loc)
                if loc_data:
                    result["Locations"][loc] = self._simplify_location(loc)

        # Player relations
        player = self.ws.player.copy()
        faction_rels = player.get("FactionRelations", [])
        filtered_faction_rels = [r for r in faction_rels if r.get("Target") in allowed_entities]
        player["FactionRelations"] = filtered_faction_rels
        npc_rels = player.get("NPCRelations", [])
        filtered_npc_rels = [r for r in npc_rels if r.get("Target") in allowed_entities]
        player["NPCRelations"] = filtered_npc_rels
        if filtered_faction_rels or filtered_npc_rels:
            result["Player"] = player

        return result

    def reduce_random(self) -> Tuple[str, str, Dict[str, Any]]:
        """Pick random NPC or faction and reduce accordingly."""
        if random.choice([True, False]):
            npc_names = list(self.ws.npcs.keys())
            if npc_names:
                name = random.choice(npc_names)
                return "npc", name, self.reduce_around_npc(name)
        faction_names = list(self.ws.factions.keys())
        if faction_names:
            name = random.choice(faction_names)
            return "faction", name, self.reduce_around_faction(name)
        return "", "", {}