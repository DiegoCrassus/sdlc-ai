/* Auto-generated from specs/. Do not edit manually. */

export interface DnD5eSheetV1 {
  character_name: string;
  player_name?: string;
  class_name?: string;
  level?: number;
  strength?: number;
  dexterity?: number;
  constitution?: number;
  intelligence?: number;
  wisdom?: number;
  charisma?: number;
  armor_class?: number;
  hit_points?: number;
  speed?: string;
  notes?: string;
}

export type PresentationType = "field_grid" | "stat_row" | "rich_text";

export interface CanvasRegion {
  id: string;
  title: string;
  order: number;
  presentation: PresentationType;
  fields: string[];
  columns: number;
}

export interface CanvasSpec {
  name: string;
  version: number;
  regions: CanvasRegion[];
}

export const dnD5eCanvas: CanvasSpec = {
  "name": "DnD5eCanvas",
  "version": 1,
  "regions": [
    {
      "id": "header",
      "title": "Personagem",
      "order": 0,
      "presentation": "field_grid",
      "fields": [
        "character_name",
        "player_name",
        "class_name",
        "level"
      ],
      "columns": 2
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
        "charisma"
      ],
      "columns": 2
    },
    {
      "id": "combat",
      "title": "Combate",
      "order": 2,
      "presentation": "field_grid",
      "fields": [
        "armor_class",
        "hit_points",
        "speed"
      ],
      "columns": 3
    },
    {
      "id": "notes",
      "title": "Anotações",
      "order": 3,
      "presentation": "rich_text",
      "fields": [
        "notes"
      ],
      "columns": 2
    }
  ]
};

export const bffV1Routes = [
  {
    "method": "GET",
    "path": "/v1/campaigns",
    "tag": "campaigns",
    "response": "CampaignListDto",
    "body": null,
    "stream": false
  },
  {
    "method": "POST",
    "path": "/v1/campaigns",
    "tag": "campaigns",
    "response": "CampaignDetailDto",
    "body": "CreateCampaignDto",
    "stream": false
  },
  {
    "method": "GET",
    "path": "/v1/campaigns/{campaign_id}",
    "tag": "campaigns",
    "response": "CampaignDetailDto",
    "body": null,
    "stream": false
  },
  {
    "method": "GET",
    "path": "/v1/campaigns/{campaign_id}/sheets",
    "tag": "campaigns",
    "response": "CampaignSheetsDto",
    "body": null,
    "stream": false
  },
  {
    "method": "GET",
    "path": "/v1/sheets/{sheet_id}",
    "tag": "campaigns",
    "response": "SheetDetailDto",
    "body": null,
    "stream": false
  },
  {
    "method": "PUT",
    "path": "/v1/sheets/{sheet_id}",
    "tag": "campaigns",
    "response": "SheetDetailDto",
    "body": "UpdateSheetDto",
    "stream": false
  },
  {
    "method": "POST",
    "path": "/v1/campaigns/{campaign_id}/template/source",
    "tag": "campaigns",
    "response": "TemplateAnalysisDto",
    "body": "TemplateSourceUploadDto",
    "stream": false
  },
  {
    "method": "POST",
    "path": "/v1/campaigns/{campaign_id}/template/publish",
    "tag": "campaigns",
    "response": "SheetTemplateDto",
    "body": "PublishTemplateDto",
    "stream": false
  },
  {
    "method": "POST",
    "path": "/v1/campaigns/{campaign_id}/template/extend",
    "tag": "campaigns",
    "response": "SheetTemplateDto",
    "body": "ExtendTemplateDto",
    "stream": false
  }
] as const;
