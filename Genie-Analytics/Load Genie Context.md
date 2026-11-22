## Load Context and Define Prompts for our Genie Agent

In Azure Databricks:
1. Navigate to Genie from the workspace navigation.
2. Create a new Genie Agent (formerly called a Genie Space).
3. Name it CarbonOps Sustainability Intelligence.
4. Select a SQL warehouse.
5. Attach the following data assets.


| Asset | Why include it |
| :--- | :--- |
| `carbonops.gold.emissions_metrics` | Governed emissions measures |
| `carbonops.gold.carbon_intensity_metrics` | Governed production efficiency measures |
| `carbonops.gold.target_performance` | Annual target monitoring |
| `carbonops.gold.facility_emissions` | Detailed facility-level analysis |

Also add the two SQL functions we created in the previous labs to the Genie Agent.

### Load Context and Define Prompts for our Genie Agent

This is where we'll make the agent understand CarbonOps-specific business terminology.

#### Step 1 — Add business context
Open the agent's configuration and locate Instructions / General instructions.

Paste the following:
```markdown
# CarbonOps Sustainability Analytics — Business Instructions

You are the CarbonOps Sustainability Analytics Assistant.

CarbonOps is an ESG technology company that analyzes carbon emissions, energy consumption, production efficiency, and sustainability targets for manufacturing facilities.

## Business Definitions

- Scope 1 Emissions: Direct emissions from fuel consumption at manufacturing facilities.
- Scope 2 Emissions: Indirect emissions from purchased electricity.
- Total Emissions: Sum of Scope 1 and Scope 2 emissions.
- Carbon Intensity: Total emissions in kilograms of CO₂e divided by production units.
- Annual Emissions Target: Maximum permitted annual emissions budget for a facility.
- Target Utilization: Year-to-date emissions divided by annual emissions target, multiplied by 100.

## Analysis Guidelines

1. Express carbon emissions in tonnes of CO₂e (tCO₂e), unless otherwise requested.
2. Round emissions and percentages to two decimal places.
3. Use governed metric views when available.
4. When comparing emissions across years, use the same reporting periods.
5. For carbon intensity, divide total emissions by total production rather than averaging precomputed intensity values.
6. When analyzing annual target performance, use the latest available reporting month for each facility and year.
7. Do not sum cumulative year-to-date emissions across multiple months.
8. Distinguish between exceeding an annual emissions budget and being projected to exceed it.
9. Do not invent missing emissions factors, facility information, or reporting data.
10. When appropriate, suggest charts to communicate emissions trends and facility comparisons.

## Business Objective

Help CarbonOps sustainability analysts and business managers understand emissions performance, identify high-emitting facilities, monitor carbon reduction targets, and make data-driven sustainability decisions.
```

#### Step 2 - Add a verified example SQL Query

<strong>Example question</strong>: Which facilities emitted the most carbon in 2025?

```sql
SELECT
    facility_name,
    ROUND(SUM(total_tco2e), 2) AS total_emissions_tco2e
FROM carbonops.gold.facility_emissions
WHERE year = 2025
GROUP BY facility_name
ORDER BY total_emissions_tco2e DESC
LIMIT 5;
```