import pytest
from httpx import AsyncClient
from src.core.config import settings
from tests.utils import upload_file, get_with_wrong_id


@pytest.mark.asyncio
async def test_files_validate_valid(client: AsyncClient, fixture_validate_files):
    assert fixture_validate_files is not None


@pytest.mark.asyncio
async def test_files_import(client: AsyncClient, fixture_validate_files):
    validate_job_ids = fixture_validate_files
    assert validate_job_ids is not None

    # Hit endpoint to upload file
    for validate_job_id in validate_job_ids:
        await upload_file(client, validate_job_id)


@pytest.mark.asyncio
async def test_files_validate_invalid(client: AsyncClient, fixture_validate_file_invalid):
    assert fixture_validate_file_invalid is not None


@pytest.mark.asyncio
async def test_create_internal_layer(client: AsyncClient, fixture_create_internal_layers):
    assert fixture_create_internal_layers is not None


@pytest.mark.asyncio
async def test_create_external_layers(client: AsyncClient, fixture_create_external_layers):
    assert fixture_create_external_layers is not None


@pytest.mark.asyncio
async def test_get_internal_layer(client: AsyncClient, fixture_create_internal_layer):
    layer_id = fixture_create_internal_layer["id"]
    response = await client.get(f"{settings.API_V2_STR}/layer/{layer_id}")
    assert response.status_code == 200
    assert response.json()["id"] == layer_id


@pytest.mark.asyncio
async def test_get_external_layer(client: AsyncClient, fixture_create_external_layer):
    layer_id = fixture_create_external_layer["id"]
    response = await client.get(f"{settings.API_V2_STR}/layer/{layer_id}")
    assert response.status_code == 200
    assert response.json()["id"] == layer_id

@pytest.mark.asyncio
async def test_get_layer_wrong_id(client: AsyncClient, fixture_create_external_layer):
    await get_with_wrong_id(client, "layer")


@pytest.mark.asyncio
async def test_update_internal_layer(client: AsyncClient, fixture_create_internal_layer):
    layer_id = fixture_create_internal_layer["id"]
    layer_dict = fixture_create_internal_layer
    layer_dict["name"] = "Updated name"
    layer_dict["description"] = "Updated description"
    layer_dict["tags"] = ["Update tag 1", "Update tag 2"]
    layer_dict["thumbnail_url"] = "https://updated-example.com"
    response = await client.put(f"{settings.API_V2_STR}/layer/{layer_id}", json=layer_dict)
    updated_layer = response.json()
    assert response.status_code == 200
    assert updated_layer["name"] == "Updated name"
    assert updated_layer["description"] == "Updated description"
    assert set(updated_layer["tags"]) == {"Update tag 1", "Update tag 2"}
    assert updated_layer["thumbnail_url"] == "https://updated-example.com"


@pytest.mark.asyncio
async def test_delete_internal_layers(client: AsyncClient, fixture_delete_internal_layers):
    return


@pytest.mark.asyncio
async def test_delete_external_layers(client: AsyncClient, fixture_delete_external_layers):
    return


# @pytest.mark.asyncio
# async def test_get_unique_values_layer(client: AsyncClient, fixture_create_internal_layer):
#     layer_id = fixture_create_internal_layer["id"]
#     column = "name"
#     response = await client.get(f"{settings.API_V2_STR}/layer/{layer_id}/{column}/unique-values")
#     assert response.status_code == 200
#     assert response.json() is not None




# Some further test cases
"""Valid File Import
Use an invalid job ID for import
Ensure the API responds with the proper HTTP error (404 Not Found)

Create multiple layers
Use the "get-by-ids" endpoint to retrieve them in bulk using their IDs
Ensure all are returned as expected
Retrieve Layers with Filters

Create multiple layers with varying attributes (different layer_type, feature_layer_type, etc.)
Use the layered retrieval endpoint with different combinations of filters
Ensure the results match the expected filtered layers"""
