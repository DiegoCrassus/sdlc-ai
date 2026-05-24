"""D&D 5e canvas layout — regions and presentation types."""

from rpg_dsl import Canvas, Field, Presentation, Region


@Canvas(version=1)
class DnD5eCanvas:
    header = Region(
        id="header",
        title="Personagem",
        order=0,
        presentation=Presentation.FIELD_GRID,
        columns=2,
        fields=[
            Field.key("character_name"),
            Field.key("player_name"),
            Field.key("class_name"),
            Field.key("level"),
        ],
    )

    attributes = Region(
        id="attributes",
        title="Atributos",
        order=1,
        presentation=Presentation.STAT_ROW,
        fields=[
            Field.key("strength"),
            Field.key("dexterity"),
            Field.key("constitution"),
            Field.key("intelligence"),
            Field.key("wisdom"),
            Field.key("charisma"),
        ],
    )

    combat = Region(
        id="combat",
        title="Combate",
        order=2,
        presentation=Presentation.FIELD_GRID,
        columns=3,
        fields=[
            Field.key("armor_class"),
            Field.key("hit_points"),
            Field.key("speed"),
        ],
    )

    notes = Region(
        id="notes",
        title="Anotações",
        order=3,
        presentation=Presentation.RICH_TEXT,
        fields=[Field.key("notes")],
    )
