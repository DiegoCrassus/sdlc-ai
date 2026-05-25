"""BFF v1 contract for the Sheet Canvas MVP flow."""

from rpg_dsl import GET, POST, PUT, api


@api(prefix="/v1", tag="campaigns")
class BffV1:
    @GET("/campaigns", response="CampaignListDto")
    def list_campaigns(self) -> None: ...

    @POST("/campaigns", response="CampaignDetailDto", body="CreateCampaignDto")
    def create_campaign(self) -> None: ...

    @GET("/campaigns/{campaign_id}", response="CampaignDetailDto")
    def get_campaign(self, campaign_id: str) -> None: ...

    @GET("/campaigns/{campaign_id}/sheets", response="CampaignSheetsDto")
    def list_campaign_sheets(self, campaign_id: str) -> None: ...

    @GET("/sheets/{sheet_id}", response="SheetDetailDto")
    def get_sheet(self, sheet_id: str) -> None: ...

    @PUT("/sheets/{sheet_id}", response="SheetDetailDto", body="UpdateSheetDto")
    def update_sheet(self, sheet_id: str) -> None: ...

    @POST(
        "/campaigns/{campaign_id}/template/source",
        response="TemplateAnalysisDto",
        body="TemplateSourceUploadDto",
    )
    def upload_template_source(self, campaign_id: str) -> None: ...

    @POST(
        "/campaigns/{campaign_id}/template/publish",
        response="SheetTemplateDto",
        body="PublishTemplateDto",
    )
    def publish_template(self, campaign_id: str) -> None: ...

    @POST(
        "/campaigns/{campaign_id}/template/extend",
        response="SheetTemplateDto",
        body="ExtendTemplateDto",
    )
    def extend_template(self, campaign_id: str) -> None: ...
