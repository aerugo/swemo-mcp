"""
Tests for the OpenAPI specification validation.
"""

import pytest
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from riksbank_mcp.openapi import MONETARY_POLICY_SPEC


def test_monetary_policy_spec_is_valid():
    """Test that the Monetary Policy OpenAPI spec is valid."""
    # Basic structure validation
    assert "openapi" in MONETARY_POLICY_SPEC
    assert "info" in MONETARY_POLICY_SPEC
    assert "paths" in MONETARY_POLICY_SPEC
    assert "components" in MONETARY_POLICY_SPEC
    
    # Check specific paths
    assert "/forecasts" in MONETARY_POLICY_SPEC["paths"]
    assert "/forecasts/policy_rounds" in MONETARY_POLICY_SPEC["paths"]
    assert "/forecasts/series_ids" in MONETARY_POLICY_SPEC["paths"]
    
    # Check components
    assert "schemas" in MONETARY_POLICY_SPEC["components"]
    assert "ForecastSeries" in MONETARY_POLICY_SPEC["components"]["schemas"]


def test_forecast_series_schema():
    """Test that the ForecastSeries schema is correctly defined."""
    forecast_schema = MONETARY_POLICY_SPEC["components"]["schemas"]["ForecastSeries"]
    
    # Check schema structure
    assert "type" in forecast_schema
    assert forecast_schema["type"] == "object"
    assert "properties" in forecast_schema
    
    # Check properties
    properties = forecast_schema["properties"]
    assert "external_id" in properties
    assert "vintages" in properties
    
    # Check vintages array
    vintages = properties["vintages"]
    assert vintages["type"] == "array"
    assert "items" in vintages
    
    # Check observations in vintages
    vintage_items = vintages["items"]
    assert "properties" in vintage_items
    assert "observations" in vintage_items["properties"]
    
    # Check observation structure
    observations = vintage_items["properties"]["observations"]
    assert observations["type"] == "array"
    assert "items" in observations
    
    # Check observation properties
    obs_items = observations["items"]
    assert "properties" in obs_items
    assert "dt" in obs_items["properties"]
    assert "value" in obs_items["properties"]
    
    # Check value is numeric
    assert obs_items["properties"]["value"]["type"] == "number"


def test_validate_example_data():
    """Test that the example data in the spec validates against the schema."""
    # Get the schema and example for /forecasts endpoint
    forecasts_path = MONETARY_POLICY_SPEC["paths"]["/forecasts"]
    response_200 = forecasts_path["get"]["responses"]["200"]
    content = response_200["content"]["application/json"]
    
    schema = content["schema"]
    example = content["example"]
    
    # Validate the example against the schema
    try:
        validate(instance=example, schema=schema)
    except ValidationError as e:
        pytest.fail(f"Example data does not validate against schema: {e}")
