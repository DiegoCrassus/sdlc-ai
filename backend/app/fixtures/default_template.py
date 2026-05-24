"""Default sheet schema, canvas spec and mock example data for new sandboxes."""

DEFAULT_SCHEMA = {
    "version": 1,
    "fields": {
        "character_name": {"type": "string", "label": "Nome do personagem", "required": True},
        "player_name": {"type": "string", "label": "Jogador"},
        "class_name": {"type": "string", "label": "Classe / Arquétipo"},
        "level": {"type": "integer", "label": "Nível", "min": 1, "max": 30},
        "strength": {"type": "integer", "label": "FOR", "min": 1, "max": 30},
        "dexterity": {"type": "integer", "label": "DES", "min": 1, "max": 30},
        "constitution": {"type": "integer", "label": "CON", "min": 1, "max": 30},
        "intelligence": {"type": "integer", "label": "INT", "min": 1, "max": 30},
        "wisdom": {"type": "integer", "label": "SAB", "min": 1, "max": 30},
        "charisma": {"type": "integer", "label": "CAR", "min": 1, "max": 30},
        "armor_class": {"type": "integer", "label": "Classe de Armadura"},
        "hit_points": {"type": "integer", "label": "Pontos de Vida"},
        "speed": {"type": "string", "label": "Deslocamento"},
        "notes": {"type": "text", "label": "Anotações"},
    },
}

DEFAULT_CANVAS_SPEC = {
    "version": 1,
    "layout": "regions",
    "regions": [
        {
            "id": "header",
            "title": "Personagem",
            "order": 0,
            "columns": 2,
            "presentation": "field_grid",
            "fields": ["character_name", "player_name", "class_name", "level"],
        },
        {
            "id": "attributes",
            "title": "Atributos",
            "order": 1,
            "presentation": "stat_row",
            "fields": [
                "strength",
                "dexterity",
                "constitution",
                "intelligence",
                "wisdom",
                "charisma",
            ],
        },
        {
            "id": "combat",
            "title": "Combate",
            "order": 2,
            "columns": 3,
            "presentation": "field_grid",
            "fields": ["armor_class", "hit_points", "speed"],
        },
        {
            "id": "notes",
            "title": "Anotações",
            "order": 3,
            "presentation": "rich_text",
            "fields": ["notes"],
        },
    ],
    "styling": {"density": "compact", "show_labels": True},
    "role_overrides": {
        "player": {"readonly_fields": []},
        "gm": {"readonly_fields": []},
    },
}

MOCK_SHEET_DATA = {
    "character_name": "Lyra Moonwhisper",
    "player_name": "Jogador exemplo",
    "class_name": "Ranger",
    "level": 5,
    "strength": 14,
    "dexterity": 18,
    "constitution": 13,
    "intelligence": 10,
    "wisdom": 15,
    "charisma": 12,
    "armor_class": 16,
    "hit_points": 38,
    "speed": "9 m",
    "notes": (
        "Exemplo mockado para demonstrar o canvas. "
        "Substitua pelos dados reais quando o template for analisado pelo agente."
    ),
}
