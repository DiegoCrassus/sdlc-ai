from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import dumps_json, get_db, loads_json
from app.deps.session import require_session
from app.models import TemplateExtension, Workspace
from app.routers.workspaces import _get_workspace_or_404, template_image_url
from app.services.dpa_analyzer import (
    TemplateAnalysisResult,
    analyze_template,
    extend_template_analysis,
)
from app.services.template_extend import (
    TemplateExtendError,
    extend_from_description,
    extend_template,
    merge_new_fields_into_sheet,
    remove_field,
)
from app.services.template_publish import (
    collect_sheet_data,
    migrate_sheets_to_template,
    schema_field_keys,
)
from app.services.template_storage import save_template_source

router = APIRouter(prefix="/workspaces", tags=["template"])


class TemplateAnalysisResponse(BaseModel):
    template_status: str
    template_version: int
    published_at: datetime | None
    analysis: dict | None
    schema_data: dict
    canvas_spec: dict
    warnings: list[str] = Field(default_factory=list)
    confidence: str | None = None
    template_image_url: str | None


class TemplateAnalysisPatch(BaseModel):
    schema_data: dict | None = None
    canvas_spec: dict | None = None
    analysis: dict | None = None


class TemplateExtendRequest(BaseModel):
    description: str | None = None
    field_key: str | None = None
    field_label: str | None = None
    field_type: str = "string"
    region_id: str | None = None
    region_title: str | None = None
    create_region: bool = False


class TemplateRemoveFieldRequest(BaseModel):
    field_key: str
    confirm: bool = False


class RemoveFieldPreview(BaseModel):
    field_key: str
    affected_sheets: int
    needs_confirm: bool


def _analysis_response(workspace: Workspace) -> TemplateAnalysisResponse:
    analysis = loads_json(workspace.analysis_json) if workspace.analysis_json else None
    warnings: list[str] = []
    confidence: str | None = None
    if isinstance(analysis, dict):
        warnings = analysis.get("warnings") or []
        confidence = analysis.get("confidence")

    return TemplateAnalysisResponse(
        template_status=workspace.template_status,
        template_version=workspace.template_version,
        published_at=workspace.published_at,
        analysis=analysis,
        schema_data=loads_json(workspace.schema_json),  # type: ignore[arg-type]
        canvas_spec=loads_json(workspace.canvas_spec_json),  # type: ignore[arg-type]
        warnings=warnings,
        confidence=confidence,
        template_image_url=template_image_url(workspace.id, workspace.template_image_path),
    )


def _apply_analysis(workspace: Workspace, result: TemplateAnalysisResult) -> None:
    workspace.analysis_json = dumps_json(result.model_dump())
    workspace.schema_json = dumps_json(result.sheet_schema)
    workspace.canvas_spec_json = dumps_json(result.canvas_spec)


@router.post("/{workspace_id}/template/source")
async def upload_template_source(
    workspace_id: str,
    source: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    workspace = await _get_workspace_or_404(db, workspace_id)
    try:
        path, mime = save_template_source(workspace_id, source)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    workspace.template_image_path = path
    workspace.source_mime = mime
    if workspace.template_status == "published" and not workspace.is_example:
        workspace.template_status = "draft"
    await db.commit()
    return {"template_image_url": template_image_url(workspace.id, path), "source_mime": mime}


@router.post("/{workspace_id}/template/analyze", response_model=TemplateAnalysisResponse)
async def analyze_workspace_template(
    workspace_id: str, db: AsyncSession = Depends(get_db)
) -> TemplateAnalysisResponse:
    workspace = await _get_workspace_or_404(db, workspace_id)
    result = analyze_template(
        sheet_source=workspace.sheet_source,
        sheet_input_raw=workspace.sheet_input_raw,
        has_image=bool(workspace.template_image_path),
    )
    _apply_analysis(workspace, result)
    workspace.template_status = "draft"
    await db.commit()
    await db.refresh(workspace)
    return _analysis_response(workspace)


@router.get("/{workspace_id}/template/analysis", response_model=TemplateAnalysisResponse)
async def get_template_analysis(
    workspace_id: str, db: AsyncSession = Depends(get_db)
) -> TemplateAnalysisResponse:
    workspace = await _get_workspace_or_404(db, workspace_id)
    return _analysis_response(workspace)


@router.patch("/{workspace_id}/template/analysis", response_model=TemplateAnalysisResponse)
async def patch_template_analysis(
    workspace_id: str,
    body: TemplateAnalysisPatch,
    db: AsyncSession = Depends(get_db),
) -> TemplateAnalysisResponse:
    workspace = await _get_workspace_or_404(db, workspace_id)
    if body.schema_data is not None:
        workspace.schema_json = dumps_json(body.schema_data)
    if body.canvas_spec is not None:
        workspace.canvas_spec_json = dumps_json(body.canvas_spec)
    if body.analysis is not None:
        workspace.analysis_json = dumps_json(body.analysis)
    workspace.template_status = "draft"
    await db.commit()
    await db.refresh(workspace)
    return _analysis_response(workspace)


def _require_gm(role: str) -> None:
    if role != "gm":
        raise HTTPException(status_code=403, detail="Apenas o mestre pode alterar o template.")


@router.post("/{workspace_id}/template/extend", response_model=TemplateAnalysisResponse)
async def extend_workspace_template(
    workspace_id: str,
    body: TemplateExtendRequest,
    session: tuple[str, str] = Depends(require_session),
    db: AsyncSession = Depends(get_db),
) -> TemplateAnalysisResponse:
    role, _ = session
    _require_gm(role)

    workspace = await _get_workspace_or_404(db, workspace_id)
    schema = loads_json(workspace.schema_json)
    canvas = loads_json(workspace.canvas_spec_json)
    if not isinstance(schema, dict) or not isinstance(canvas, dict):
        raise HTTPException(status_code=500, detail="Schema inválido.")

    previous_keys = schema_field_keys(schema)

    try:
        if body.field_label:
            key = body.field_key or body.field_label
            new_schema, new_canvas, patch = extend_template(
                schema,
                canvas,
                field_key=key,
                field_label=body.field_label,
                field_type=body.field_type,
                region_id=body.region_id,
                region_title=body.region_title,
                create_region=body.create_region,
                description=body.description or "",
            )
        elif body.description:
            new_schema, new_canvas, patch = extend_from_description(schema, canvas, body.description)
        else:
            raise TemplateExtendError("Informe description ou field_key + field_label.")
    except TemplateExtendError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    result = extend_template_analysis(
        new_schema,
        new_canvas,
        patch,
        description=body.description or patch.get("field_label", ""),
    )
    _apply_analysis(workspace, result)
    workspace.schema_json = dumps_json(new_schema)
    workspace.canvas_spec_json = dumps_json(new_canvas)
    workspace.template_status = "draft"

    if workspace.example_sheet:
        data = loads_json(workspace.example_sheet.data_json)
        if isinstance(data, dict):
            workspace.example_sheet.data_json = dumps_json(
                merge_new_fields_into_sheet(data, new_schema, previous_keys)
            )

    db.add(
        TemplateExtension(
            workspace_id=workspace.id,
            from_version=workspace.template_version,
            patch_json=dumps_json(patch),
            description=body.description or patch.get("field_label", ""),
        )
    )
    await db.commit()
    await db.refresh(workspace)
    return _analysis_response(workspace)


@router.post("/{workspace_id}/template/remove-field", response_model=TemplateAnalysisResponse)
async def remove_template_field(
    workspace_id: str,
    body: TemplateRemoveFieldRequest,
    session: tuple[str, str] = Depends(require_session),
    db: AsyncSession = Depends(get_db),
) -> TemplateAnalysisResponse:
    role, _ = session
    _require_gm(role)

    workspace = await _get_workspace_or_404(db, workspace_id)
    schema = loads_json(workspace.schema_json)
    canvas = loads_json(workspace.canvas_spec_json)
    if not isinstance(schema, dict) or not isinstance(canvas, dict):
        raise HTTPException(status_code=500, detail="Schema inválido.")

    sheet_data = await collect_sheet_data(db, workspace.id)
    if workspace.example_sheet:
        ex_data = loads_json(workspace.example_sheet.data_json)
        if isinstance(ex_data, dict):
            sheet_data.append(ex_data)

    try:
        new_schema, new_canvas, patch = remove_field(
            schema,
            canvas,
            body.field_key,
            sheet_data,
            confirm=body.confirm,
        )
    except TemplateExtendError as exc:
        status = 409 if exc.needs_confirm else 400
        raise HTTPException(status_code=status, detail=str(exc)) from exc

    result = extend_template_analysis(
        new_schema,
        new_canvas,
        patch,
        description=f"Remover campo {body.field_key}",
    )
    _apply_analysis(workspace, result)
    workspace.schema_json = dumps_json(new_schema)
    workspace.canvas_spec_json = dumps_json(new_canvas)
    workspace.template_status = "draft"

    if workspace.example_sheet:
        data = loads_json(workspace.example_sheet.data_json)
        if isinstance(data, dict) and body.field_key in data:
            data = {k: v for k, v in data.items() if k != body.field_key}
            workspace.example_sheet.data_json = dumps_json(data)

    db.add(
        TemplateExtension(
            workspace_id=workspace.id,
            from_version=workspace.template_version,
            patch_json=dumps_json(patch),
            description=f"remove:{body.field_key}",
        )
    )
    await db.commit()
    await db.refresh(workspace)
    return _analysis_response(workspace)


@router.get("/{workspace_id}/template/remove-field/{field_key}/preview", response_model=RemoveFieldPreview)
async def preview_remove_field(
    workspace_id: str,
    field_key: str,
    session: tuple[str, str] = Depends(require_session),
    db: AsyncSession = Depends(get_db),
) -> RemoveFieldPreview:
    role, _ = session
    _require_gm(role)

    workspace = await _get_workspace_or_404(db, workspace_id)
    sheet_data = await collect_sheet_data(db, workspace.id)
    if workspace.example_sheet:
        ex_data = loads_json(workspace.example_sheet.data_json)
        if isinstance(ex_data, dict):
            sheet_data.append(ex_data)

    from app.services.template_extend import field_has_data

    affected = sum(1 for data in sheet_data if field_has_data(data, field_key))
    return RemoveFieldPreview(
        field_key=field_key,
        affected_sheets=affected,
        needs_confirm=affected > 0,
    )


@router.post("/{workspace_id}/template/publish", response_model=TemplateAnalysisResponse)
async def publish_template(
    workspace_id: str, db: AsyncSession = Depends(get_db)
) -> TemplateAnalysisResponse:
    workspace = await _get_workspace_or_404(db, workspace_id)
    if not workspace.analysis_json and workspace.sheet_source in {"file", "text"}:
        raise HTTPException(
            status_code=400,
            detail="Execute a análise do template antes de publicar.",
        )

    schema = loads_json(workspace.schema_json)
    if not isinstance(schema, dict) or not schema.get("fields"):
        raise HTTPException(status_code=400, detail="Schema vazio — analise ou corrija o template.")

    analysis_raw = loads_json(workspace.analysis_json) if workspace.analysis_json else {}
    analysis: dict = analysis_raw if isinstance(analysis_raw, dict) else {}
    previous_keys = set(analysis.get("last_published_field_keys") or [])

    workspace.template_status = "published"
    workspace.template_version += 1
    workspace.published_at = datetime.now(timezone.utc)

    await migrate_sheets_to_template(
        db, workspace, schema, previous_field_keys=previous_keys
    )

    published_analysis = loads_json(workspace.analysis_json) if workspace.analysis_json else {}
    if not isinstance(published_analysis, dict):
        published_analysis = {}
    published_analysis["last_published_field_keys"] = list(schema_field_keys(schema))
    workspace.analysis_json = dumps_json(published_analysis)

    if workspace.example_sheet:
        workspace.example_sheet.label = f"Ficha exemplo — template v{workspace.template_version}"

    await db.commit()
    await db.refresh(workspace)
    return _analysis_response(workspace)
