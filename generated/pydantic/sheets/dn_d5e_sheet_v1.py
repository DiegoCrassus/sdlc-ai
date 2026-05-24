from pydantic import BaseModel, Field


class DnD5eSheetV1(BaseModel):
    character_name: str = Field(..., title="Nome do personagem")
    player_name: str | None = Field(None, title="Jogador")
    class_name: str | None = Field(None, title="Classe / Arquétipo")
    level: int | None = Field(None, title="Nível")
    strength: int | None = Field(None, title="FOR")
    dexterity: int | None = Field(None, title="DES")
    constitution: int | None = Field(None, title="CON")
    intelligence: int | None = Field(None, title="INT")
    wisdom: int | None = Field(None, title="SAB")
    charisma: int | None = Field(None, title="CAR")
    armor_class: int | None = Field(None, title="Classe de Armadura")
    hit_points: int | None = Field(None, title="Pontos de Vida")
    speed: str | None = Field(None, title="Deslocamento")
    notes: str | None = Field(None, title="Anotações")
