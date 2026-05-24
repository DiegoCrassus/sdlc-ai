"""D&D 5e sheet schema — source of truth for field definitions."""

from rpg_dsl import Sheet, sheet_field

@Sheet(version=1)
class DnD5eSheet:
    character_name = sheet_field("character_name", "Nome do personagem", required=True)
    player_name    = sheet_field("player_name",    "Jogador")
    class_name     = sheet_field("class_name",     "Classe / Arquétipo")
    level          = sheet_field("level",          "Nível",  type="integer", min=1, max=30)

    strength      = sheet_field("strength",      "FOR", type="integer", min=1, max=30)
    dexterity     = sheet_field("dexterity",     "DES", type="integer", min=1, max=30)
    constitution  = sheet_field("constitution",  "CON", type="integer", min=1, max=30)
    intelligence  = sheet_field("intelligence",  "INT", type="integer", min=1, max=30)
    wisdom        = sheet_field("wisdom",        "SAB", type="integer", min=1, max=30)
    charisma      = sheet_field("charisma",      "CAR", type="integer", min=1, max=30)

    armor_class = sheet_field("armor_class", "Classe de Armadura", type="integer")
    hit_points  = sheet_field("hit_points",  "Pontos de Vida",     type="integer")
    speed       = sheet_field("speed",       "Deslocamento")
    notes       = sheet_field("notes",       "Anotações", type="text")
