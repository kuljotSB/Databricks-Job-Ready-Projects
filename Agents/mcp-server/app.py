
from typing import Any, Dict
import os
import math

from mcp.server.fastmcp import FastMCP
from databricks.sdk import WorkspaceClient

# Setting up the endpoint environment variables
EMISSIONS_ENDPOINT = os.environ["EMISSIONS_ENDPOINT"]
RISK_ENDPOINT = os.environ["RISK_ENDPOINT"]

# Uses Databricks App service principal credentials
workspace = WorkspaceClient()

# Initialize MCP server
mcp = FastMCP(
    name="carbonops-sustainability-mcp",
    host="0.0.0.0",
    port=8000,
    stateless_http=True
)

# Model Feature Definitions
EMISSIONS_FEATURES = [
    "year",
    "month",
    "electricity_kwh",
    "diesel_litres",
    "natural_gas_m3",
    "lpg_kg",
    "production_units",
    "operating_hours",
    "avg_temperature_c"
]

RISK_FEATURES = EMISSIONS_FEATURES + [
    "current_emissions_tco2e",
    "previous_month_emissions_tco2e",
    "monthly_emissions_budget_tco2e"
]

# Helper function to validate inputs
def validate_features(features: Dict[str, Any]) -> None:

    if not 1 <= features["month"] <= 12:
        raise ValueError("Month must be between 1 and 12")

    if not 2000 <= features["year"] <= 2100:
        raise ValueError("Year must be between 2000 and 2100")

    for name, value in features.items():

        if isinstance(value, bool) or not isinstance(
            value, (int, float)
        ):
            raise ValueError(f"{name} must be numeric")

        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")

        if name not in [
            "year", "month", "avg_temperature_c"
        ] and value < 0:
            raise ValueError(f"{name} cannot be negative")


# Helper function: Invoke Databricks Serving Endpoint
import logging
from databricks.sdk.service.serving import DataframeSplitInput

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("carbonops-mcp")


def call_model(
    endpoint: str,
    features: Dict[str, Any]
) -> Any:

    try:
        logger.info("Calling endpoint: %s", endpoint)
        logger.info("Features: %s", features)

        payload = DataframeSplitInput(
            columns=list(features.keys()),
            data=[list(features.values())]
        )

        response = workspace.serving_endpoints.query(
            name=endpoint,
            dataframe_split=payload
        )

        logger.info("Model response: %s", response)

        if not response.predictions:
            raise RuntimeError(
                f"No predictions returned from {endpoint}"
            )

        return response.predictions[0]

    except Exception:
        logger.exception(
            "Model Serving call failed for %s",
            endpoint
        )
        raise


# Helper function: Extract Regression Prediction
def extract_emissions(result: Any) -> float:

    if isinstance(result, dict):
        result = result.get(
            "prediction",
            result.get("predicted_emissions_tco2e")
        )

    if result is None:
        raise ValueError("Missing regression prediction")

    value = float(result)

    if not math.isfinite(value):
        raise ValueError("Invalid regression prediction")

    return value

# Helper function: Extract Classification Prediction
def extract_risk(result: Any) -> Dict[str, Any]:

    probability = None

    if isinstance(result, dict):

        predicted_class = result.get("prediction")
        probabilities = result.get("probability")

        if probabilities is not None:
            probability = float(probabilities[1])

        if predicted_class is None and probability is not None:
            predicted_class = int(probability >= 0.5)

    else:
        predicted_class = result

    if predicted_class is None:
        raise ValueError("Missing classification prediction")

    predicted_class = int(predicted_class)

    if predicted_class not in (0, 1):
        raise ValueError("Expected binary classification")

    if probability is not None and not 0 <= probability <= 1:
        raise ValueError("Invalid probability returned")

    return {
        "predicted_risk": predicted_class,
        "risk_probability": (
            round(probability, 4)
            if probability is not None
            else None
        ),
        "risk_status": (
            "AT RISK"
            if predicted_class == 1
            else "LOW RISK"
        )
    }

# Tool 1: Predict Carbon Emissions
@mcp.tool(
    name="predict_carbon_emissions",
    description=(
        "Predict monthly manufacturing carbon emissions "
        "in tonnes of CO2e using the CarbonOps "
        "Ridge Regression model."
    ),
    structured_output=True
)
def predict_carbon_emissions(
    year: int,
    month: int,
    electricity_kwh: float,
    diesel_litres: float,
    natural_gas_m3: float,
    lpg_kg: float,
    production_units: float,
    operating_hours: float,
    avg_temperature_c: float
) -> Dict[str, Any]:

    features = {
        "year": year,
        "month": month,
        "electricity_kwh": electricity_kwh,
        "diesel_litres": diesel_litres,
        "natural_gas_m3": natural_gas_m3,
        "lpg_kg": lpg_kg,
        "production_units": production_units,
        "operating_hours": operating_hours,
        "avg_temperature_c": avg_temperature_c
    }

    validate_features(features)

    result = call_model(
        EMISSIONS_ENDPOINT,
        features
    )

    emissions = extract_emissions(result)

    return {
        "model": "CarbonOps Ridge Regression",
        "predicted_emissions_tco2e": round(emissions, 2),
        "unit": "tCO2e",
        "year": year,
        "month": month
    }

# Tool 2: Predict Carbon Emissions Risk
@mcp.tool(
    name="predict_emissions_risk",
    description=(
        "Predict whether a manufacturing facility will "
        "exceed its monthly carbon budget in the following "
        "month using the CarbonOps Logistic Regression model."
    ),
    structured_output=True
)
def predict_emissions_risk(
    year: int,
    month: int,
    electricity_kwh: float,
    diesel_litres: float,
    natural_gas_m3: float,
    lpg_kg: float,
    production_units: float,
    operating_hours: float,
    avg_temperature_c: float,
    current_emissions_tco2e: float,
    previous_month_emissions_tco2e: float,
    monthly_emissions_budget_tco2e: float
) -> Dict[str, Any]:

    features = {
        "year": year,
        "month": month,
        "electricity_kwh": electricity_kwh,
        "diesel_litres": diesel_litres,
        "natural_gas_m3": natural_gas_m3,
        "lpg_kg": lpg_kg,
        "production_units": production_units,
        "operating_hours": operating_hours,
        "avg_temperature_c": avg_temperature_c,
        "current_emissions_tco2e":
            current_emissions_tco2e,
        "previous_month_emissions_tco2e":
            previous_month_emissions_tco2e,
        "monthly_emissions_budget_tco2e":
            monthly_emissions_budget_tco2e
    }

    validate_features(features)

    result = call_model(
        RISK_ENDPOINT,
        features
    )

    risk = extract_risk(result)

    return {
        "model": "CarbonOps Logistic Regression",
        **risk,
        "current_emissions_tco2e":
            current_emissions_tco2e,
        "monthly_budget_tco2e":
            monthly_emissions_budget_tco2e,
        "forecast_horizon": "Next month"
    }

# Tool 3: Calculate Carbon Intensity
@mcp.tool(
    name="calculate_carbon_intensity",
    description=(
        "Calculate manufacturing carbon intensity in "
        "kg CO2e per unit and compare against a target."
    ),
    structured_output=True
)
def calculate_carbon_intensity(
    total_emissions_tco2e: float,
    production_units: float,
    target_intensity_kg_per_unit: float
) -> Dict[str, Any]:

    if not all(math.isfinite(x) for x in [
        total_emissions_tco2e,
        production_units,
        target_intensity_kg_per_unit
    ]):
        raise ValueError("All inputs must be finite")

    if total_emissions_tco2e < 0:
        raise ValueError("Emissions cannot be negative")

    if production_units <= 0:
        raise ValueError("Production must be positive")

    if target_intensity_kg_per_unit <= 0:
        raise ValueError("Target must be positive")

    carbon_intensity = (
        total_emissions_tco2e * 1000
    ) / production_units

    variance = (
        (carbon_intensity - target_intensity_kg_per_unit)
        / target_intensity_kg_per_unit
    ) * 100

    target_achieved = (
        carbon_intensity <= target_intensity_kg_per_unit
    )

    return {
        "carbon_intensity_kg_per_unit": round(
            carbon_intensity, 3
        ),
        "target_intensity_kg_per_unit":
            target_intensity_kg_per_unit,
        "variance_percent": round(variance, 2),
        "target_achieved": target_achieved,
        "status": (
            "TARGET ACHIEVED"
            if target_achieved
            else "ABOVE TARGET"
        )
    }

# Tool 4: Simulate Emissions Reduction
@mcp.tool(
    name="simulate_emissions_reduction",
    description=(
        "Simulate changes in manufacturing emissions "
        "after reducing electricity, diesel, natural gas, "
        "or LPG consumption using the Ridge Regression model."
    ),
    structured_output=True
)
def simulate_emissions_reduction(
    year: int,
    month: int,
    electricity_kwh: float,
    diesel_litres: float,
    natural_gas_m3: float,
    lpg_kg: float,
    production_units: float,
    operating_hours: float,
    avg_temperature_c: float,
    electricity_reduction_percent: float = 0.0,
    diesel_reduction_percent: float = 0.0,
    natural_gas_reduction_percent: float = 0.0,
    lpg_reduction_percent: float = 0.0
) -> Dict[str, Any]:

    reductions = {
        "electricity_kwh": electricity_reduction_percent,
        "diesel_litres": diesel_reduction_percent,
        "natural_gas_m3": natural_gas_reduction_percent,
        "lpg_kg": lpg_reduction_percent
    }

    for name, percentage in reductions.items():
        if not math.isfinite(percentage) or not 0 <= percentage <= 100:
            raise ValueError(
                f"{name} reduction must be between 0 and 100"
            )

    baseline = {
        "year": year,
        "month": month,
        "electricity_kwh": electricity_kwh,
        "diesel_litres": diesel_litres,
        "natural_gas_m3": natural_gas_m3,
        "lpg_kg": lpg_kg,
        "production_units": production_units,
        "operating_hours": operating_hours,
        "avg_temperature_c": avg_temperature_c
    }

    validate_features(baseline)

    # Predict original emissions
    baseline_emissions = extract_emissions(
        call_model(EMISSIONS_ENDPOINT, baseline)
    )

    # Modify activity data for what-if scenario
    scenario = baseline.copy()

    for feature, percentage in reductions.items():
        scenario[feature] *= (1 - percentage / 100)

    # Predict emissions after reductions
    scenario_emissions = extract_emissions(
        call_model(EMISSIONS_ENDPOINT, scenario)
    )

    emissions_saved = (
        baseline_emissions - scenario_emissions
    )

    reduction_percent = (
        (emissions_saved / baseline_emissions) * 100
        if baseline_emissions > 0
        else None
    )

    return {
        "baseline_emissions_tco2e": round(
            baseline_emissions, 2
        ),
        "scenario_emissions_tco2e": round(
            scenario_emissions, 2
        ),
        "estimated_emissions_saved_tco2e": round(
            emissions_saved, 2
        ),
        "estimated_reduction_percent": (
            round(reduction_percent, 2)
            if reduction_percent is not None
            else None
        ),
        "consumption_reductions_percent": reductions,
        "note": (
            "Model-based estimate only. Negative savings "
            "indicate the scenario increased predicted emissions."
        )
    }

# Start MCP Server
if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        mount_path="/mcp"
    )
