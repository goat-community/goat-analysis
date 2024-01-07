from fastapi import APIRouter, Body, Depends

from src.core.tool import CRUDToolBase, start_calculation
from src.crud.crud_data_management import CRUDJoin
from src.crud.crud_geoanalysis import CRUDAggregatePoint, CRUDAggregatePolygon
from src.schemas.error import http_error_handler
from src.schemas.job import JobType, Msg
from src.schemas.tool import (
    IAggregationPoint,
    IAggregationPolygon,
    IJoin,
    request_examples_aggregation_point,
    request_examples_aggregation_polygon,
    request_examples_join,
)
from src.schemas.toolbox_base import (
    CommonToolParams,
    IToolResponse,
    ToolsWithReferenceAreaCheck,
)

router = APIRouter()


@router.post(
    "/check-reference-area",
    summary="Check reference area",
    response_model=Msg,
    status_code=200,
)
async def check_reference_area(
    common: CommonToolParams = Depends(),
    layer_project_id: int = Body(
        ...,
        title="Layer Project ID",
        description="The ID of the layer project.",
    ),
    tool_type: ToolsWithReferenceAreaCheck = Body(
        ...,
        title="Tool Type",
        description="The type of the tool.",
    ),
):
    """Check if the reference area is suitable for the requested tool operation."""
    # Catch exception nand return HTTP error message
    crud_tool_base = CRUDToolBase(
        job_id=None,
        background_tasks=common.background_tasks,
        async_session=common.async_session,
        user_id=common.user_id,
        project_id=common.project_id,
    )
    # Excute and handle exception
    result = await http_error_handler(
        crud_tool_base.check_reference_area,
        layer_project_id=layer_project_id,
        tool_type=tool_type,
    )
    return result["msg"]


@router.post(
    "/join",
    summary="Join two layers.",
    response_model=IToolResponse,
    status_code=201,
)
async def join(
    common: CommonToolParams = Depends(),
    params: IJoin = Body(
        ...,
        examples=request_examples_join,
        description="The join paramaters.",
    ),
):
    """Join two layers based on a matching column and create a new layer containing the attributes of the target layer and the new column for the statistics results."""

    return await start_calculation(
        job_type=JobType.join,
        tool_class=CRUDJoin,
        crud_method="join_run",
        async_session=common.async_session,
        user_id=common.user_id,
        background_tasks=common.background_tasks,
        project_id=common.project_id,
        params=params,
    )


@router.post(
    "/aggregate-points",
    summary="Aggregate points",
    response_model=IToolResponse,
    status_code=201,
)
async def aggregate_points(
    *,
    common: CommonToolParams = Depends(),
    params: IAggregationPoint = Body(
        ...,
        examples=request_examples_aggregation_point,
        description="The aggregation parameters.",
    ),
):
    """Aggregate points and compute statistics on a group by column."""
    return await start_calculation(
        job_type=JobType.aggregate_point,
        tool_class=CRUDAggregatePoint,
        crud_method="aggregate_point_run",
        async_session=common.async_session,
        user_id=common.user_id,
        background_tasks=common.background_tasks,
        project_id=common.project_id,
        params=params,
    )


@router.post(
    "/aggregate-polygons",
    summary="Aggregate polygons",
    response_model=IToolResponse,
    status_code=201,
)
async def aggregate_polygons(
    *,
    common: CommonToolParams = Depends(),
    params: IAggregationPolygon = Body(
        ...,
        examples=request_examples_aggregation_polygon,
        description="The aggregation parameters.",
    ),
):
    """Aggregate polygons and compute statistics on a group by column."""
    return await start_calculation(
        job_type=JobType.aggregate_polygon,
        tool_class=CRUDAggregatePolygon,
        crud_method="aggregate_polygon_run",
        async_session=common.async_session,
        user_id=common.user_id,
        background_tasks=common.background_tasks,
        project_id=common.project_id,
        params=params,
    )
