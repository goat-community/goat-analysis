import pytest
from typing import List
from httpx import AsyncClient
from src.core.config import settings
from tests.utils import check_job_status
from src.schemas.catchment_area import (
    CatchmentAreaRoutingModeActiveMobility,
    CatchmentAreaRoutingModePT,
)
from src.schemas.toolbox_base import PTSupportedDay


@pytest.mark.parametrize(
    "starting_points_type,access_mode,speed,max_traveltime,mode,weekday,from_time,to_time",
    [
        (
            "point_single",
            CatchmentAreaRoutingModeActiveMobility.walking.value, 5, 15,
            [CatchmentAreaRoutingModePT.bus.value, CatchmentAreaRoutingModePT.tram.value, CatchmentAreaRoutingModePT.subway.value, CatchmentAreaRoutingModePT.rail.value],
            PTSupportedDay.weekday.value, 25200, 32400
        ),
        (
            "point_single",
            CatchmentAreaRoutingModeActiveMobility.pedelec.value, 23, 8,
            [CatchmentAreaRoutingModePT.funicular.value, CatchmentAreaRoutingModePT.gondola.value],
            PTSupportedDay.sunday.value, 61200, 79200
        ),
        (
            "point_multiple",
            CatchmentAreaRoutingModeActiveMobility.walking.value, 7, 13,
            [CatchmentAreaRoutingModePT.bus.value, CatchmentAreaRoutingModePT.tram.value, CatchmentAreaRoutingModePT.subway.value, CatchmentAreaRoutingModePT.rail.value],
            PTSupportedDay.saturday.value, 25200, 32400
        ),
        (
            "point_multiple",
            CatchmentAreaRoutingModeActiveMobility.bicycle.value, 15, 11,
            [CatchmentAreaRoutingModePT.tram.value, CatchmentAreaRoutingModePT.ferry.value, CatchmentAreaRoutingModePT.cable_car.value, CatchmentAreaRoutingModePT.rail.value],
            PTSupportedDay.weekday.value, 68400, 82800
        ),
        (
            "point_layer",
            CatchmentAreaRoutingModeActiveMobility.walking.value, 13, 5,
            [CatchmentAreaRoutingModePT.bus.value, CatchmentAreaRoutingModePT.tram.value, CatchmentAreaRoutingModePT.subway.value, CatchmentAreaRoutingModePT.rail.value],
            PTSupportedDay.saturday.value, 46800, 57600
        ),
        (
            "point_layer",
            CatchmentAreaRoutingModeActiveMobility.pedelec.value, 20, 15,
            [CatchmentAreaRoutingModePT.subway.value, CatchmentAreaRoutingModePT.rail.value, CatchmentAreaRoutingModePT.ferry.value],
            PTSupportedDay.weekday.value, 25200, 61200
        ),
    ]
)
async def test_nearby_station_access(
        client: AsyncClient,
        fixture_create_project,
        fixture_add_aggregate_point_layer_to_project,
        starting_points_type: str,
        access_mode: str,
        speed: float,
        max_traveltime: int,
        mode: List[str],
        weekday: str,
        from_time: int,
        to_time: int,
):
    # Generate sample layers for conducting the test
    if starting_points_type == "point_single":
        project_id = fixture_create_project["id"]
        starting_points = {"latitude": [48.138577], "longitude": [11.561173]}
    elif starting_points_type == "point_multiple":
        project_id = fixture_create_project["id"]
        starting_points = {"latitude": [48.800548, 48.802696, 48.786122], "longitude": [9.180397, 9.181044, 9.201984]}
    else:
        project_id = fixture_add_aggregate_point_layer_to_project["project_id"]
        layer_project_id = fixture_add_aggregate_point_layer_to_project["source_layer_project_id"]
        starting_points = {"layer_project_id": layer_project_id}

    # Produce nearby stations access request payload
    params = {
        "starting_points": starting_points,
        "access_mode": access_mode,
        "speed": speed,
        "max_traveltime": max_traveltime,
        "mode": mode,
        "time_window": {
            "weekday": weekday,
            "from_time": from_time,
            "to_time": to_time,
        },
    }

    # Call endpoint
    response = await client.post(
        f"{settings.API_V2_STR}/motorized-mobility/nearby-station-access?project_id={project_id}",
        json=params,
    )
    assert response.status_code == 201

    # Check if job is finished
    job = await check_job_status(client, response.json()["job_id"])
    assert job["status_simple"] == "finished"
