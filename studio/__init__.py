"""SDLC Studio Python interfaces."""

from studio.canvas_view_model import (
    CanvasViewModel,
    build_canvas_from_sources,
    build_canvas_view_model,
    render_canvas_text,
)
from studio.compiler_core import (
    CompilerInputError,
    CompilerResult,
    compile_studio_sources,
)
from studio.validation_inspection import (
    ValidationInspectionInputError,
    ValidationInspectionModel,
    build_validation_inspection_from_sources,
    build_validation_inspection_model,
    render_validation_inspection_text,
)
from studio.validator_core import (
    ValidationRunResult,
    validate_compiler_result,
    validate_studio_sources,
)

__all__ = [
    "CompilerInputError",
    "CompilerResult",
    "CanvasViewModel",
    "ValidationInspectionInputError",
    "ValidationInspectionModel",
    "ValidationRunResult",
    "build_canvas_from_sources",
    "build_canvas_view_model",
    "build_validation_inspection_from_sources",
    "build_validation_inspection_model",
    "compile_studio_sources",
    "render_canvas_text",
    "render_validation_inspection_text",
    "validate_compiler_result",
    "validate_studio_sources",
]
