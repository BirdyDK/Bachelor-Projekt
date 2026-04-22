from typing import Dict, Any, List, Optional, Tuple

class WorldState:
    def __init__(self, data: Dict[str, Any]):
        self.enums = data.get("enums", {})
        self.npcs = data.get("npcs", {})
        self.factions = data.get("factions", {})
        self.enemies = data.get("enemies", {})
        self.locations = data.get("locations", {})
        self.items = data.get("items", {})
        self.player = data.get("player", {})
        
        # Handle Player field – can be list or string
        player_data = self.enums.get("Lists", {}).get("Player", [])
        if isinstance(player_data, list) and player_data:
            self.player_name = player_data[0]
        elif isinstance(player_data, str):
            self.player_name = player_data
        else:
            self.player_name = "Player"  # fallback

    def get_relation(self, giver_type: str, giver_name: str, target: str = None) -> int:
        if target is None:
            target = self.player_name

        if giver_type == "npc":
            npc = self.npcs.get(giver_name)
            if not npc:
                return 0
            personal = 0
            for rel in npc.get("Relations", []):
                if rel.get("Target") == target:
                    personal = rel.get("Favorability", 0)
                    break
            faction_name = npc.get("Faction")
            if faction_name:
                faction_rel = self.get_relation("faction", faction_name, target)
                return (personal + faction_rel) // 2
            else:
                return personal
        elif giver_type == "faction":
            faction = self.factions.get(giver_name)
            if not faction:
                return 0
            for rel in faction.get("Relations", []):
                if rel.get("Target") == target:
                    return rel.get("Favorability", 0)
            return 0
        return 0

    def get_npc_location(self, npc_name: str) -> str:
        return self.npcs.get(npc_name, {}).get("CurrentLocation", "Unknown")

    def get_faction_members(self, faction_name: str) -> List[str]:
        return self.factions.get(faction_name, {}).get("Members", [])

    def get_friendly_factions(self, faction_name: str) -> List[str]:
        faction = self.factions.get(faction_name)
        if not faction:
            return []
        friends = []
        for rel in faction.get("Relations", []):
            if rel.get("Favorability", 0) > 0 and rel["Target"] in self.factions:
                friends.append(rel["Target"])
        return friends

    def get_all_locations_with_enemies(self) -> List[Tuple[str, List[str]]]:
        return [(loc, data.get("Enemies", [])) for loc, data in self.locations.items() if data.get("Enemies")]

    def get_npcs_with_negative_relation(self, giver_type: str, giver_name: str) -> List[str]:
        result = []
        if giver_type == "npc":
            npc = self.npcs.get(giver_name)
            if not npc:
                return []
            for rel in npc.get("Relations", []):
                if rel.get("Favorability", 0) < 0 and rel["Target"] in self.npcs:
                    result.append(rel["Target"])
        elif giver_type == "faction":
            faction = self.factions.get(giver_name)
            if not faction:
                return []
            for rel in faction.get("Relations", []):
                if rel.get("Favorability", 0) < 0 and rel["Target"] in self.npcs:
                    result.append(rel["Target"])
        return result

    def get_npcs_with_high_negative_relation(self, giver_type: str, giver_name: str, threshold: int = -26) -> List[str]:
        result = []
        if giver_type == "npc":
            npc = self.npcs.get(giver_name)
            if not npc:
                return []
            for rel in npc.get("Relations", []):
                if rel.get("Favorability", 0) <= threshold and rel["Target"] in self.npcs:
                    result.append(rel["Target"])
        elif giver_type == "faction":
            faction = self.factions.get(giver_name)
            if not faction:
                return []
            for rel in faction.get("Relations", []):
                if rel.get("Favorability", 0) <= threshold and rel["Target"] in self.npcs:
                    result.append(rel["Target"])
        return result

    def get_giver_items(self, giver_type: str, giver_name: str) -> List[str]:
        if giver_type == "npc":
            return list(self.npcs.get(giver_name, {}).get("OwnedItems", {}).keys())
        elif giver_type == "faction":
            return list(self.factions.get(giver_name, {}).get("Treasury", {}).keys())
        return []
    
    def get_factions_with_negative_relation(self, giver_type: str, giver_name: str) -> List[str]:
        """Return factions that giver dislikes."""
        result = []
        if giver_type == "npc":
            npc = self.npcs.get(giver_name)
            if not npc:
                return []
            for rel in npc.get("Relations", []):
                if rel.get("Favorability", 0) < 0 and rel["Target"] in self.factions:
                    result.append(rel["Target"])
        elif giver_type == "faction":
            faction = self.factions.get(giver_name)
            if not faction:
                return []
            for rel in faction.get("Relations", []):
                if rel.get("Favorability", 0) < 0 and rel["Target"] in self.factions:
                    result.append(rel["Target"])
        return result

    def get_faction_location(self, faction_name: str) -> str:
        """Return the default location of a faction, or fallback to the current location of its first member."""
        faction = self.factions.get(faction_name)
        if faction:
            loc = faction.get("Default_Location")
            if loc:
                return loc
            # Fallback to first member's location
            members = faction.get("Members", [])
            if members:
                return self.get_npc_location(members[0])
        # Final fallback
        return "unknown"

    def get_non_friendly_entities(self, giver_type: str, giver_name: str) -> List[Tuple[str, str]]:
        """Return all entities (NPC or Faction) that giver dislikes (relation < 0)."""
        result = []
        # NPC enemies
        for npc in self.get_npcs_with_negative_relation(giver_type, giver_name):
            result.append(("npc", npc))
        # Faction enemies
        for faction in self.get_factions_with_negative_relation(giver_type, giver_name):
            result.append(("faction", faction))
        return result