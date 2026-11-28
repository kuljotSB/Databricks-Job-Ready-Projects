## Query the Genie Agent for AI/BI Data Analysis

For the final lab, we'll play the role of a CarbonOps sustainability manager and perform a series of increasingly complex analyses.

### Scenario - Emissions Overview

1) What were our total Scope 1 and Scope 2 emissions in 2025?
2) Show monthly carbon emissions trends for 2025.
3) Which five cities generated the highest total emissions?

### Scenario - Facility Performance

1) Which five facilities have the highest carbon footprint in 2025?
2) Compare Scope 1 and Scope 2 emissions for facilities in Mumbai.
3) Which facilities have the lowest carbon intensity in 2025?

### Scenario - Target Monitoring

1) Which facilities exceeded their annual emissions targets in 2025?
2) What percentage of the annual carbon budget has each facility used?
3) Show the facilities with the highest target utilization percentage in 2025.

### Scenario - Advanced Analysis

1) Compare total emissions between 2024 and 2025 for facilities with data in both years.
2) Which facilities increased their emissions between 2024 and 2025?
3) Show a monthly trend of carbon intensity for the five highest-emitting facilities.

### Create Analytics Dashboard

Use the query to create Sustainability Intelligence Dashboard using Genie:
```
Create a professional, interactive **CarbonOps Sustainability Intelligence Dashboard** using the available Gold-layer datasets in Databricks.

The dashboard should help sustainability managers monitor carbon emissions, energy consumption, manufacturing performance, and progress toward emissions reduction targets across CarbonOps facilities.

### 1. Executive KPI Overview
Display KPI cards for:
- Total Carbon Emissions (tCO₂e)
- Total Electricity Consumption (kWh)
- Total Production Units
- Average Carbon Intensity (kg CO₂e/unit)
- Total Scope 1 and Scope 2 Emissions
- Number of Facilities Monitored

### 2. Carbon Emissions Analysis
- Line chart showing monthly carbon emissions trends.
- Bar chart comparing total emissions across manufacturing facilities.
- Donut chart showing Scope 1 vs. Scope 2 emissions.
- Bar chart showing emissions by city or state.

### 3. Carbon Intensity & Manufacturing Performance
- Bar chart comparing carbon intensity across facilities.
- Trend chart showing monthly carbon intensity.
- Table displaying facility-level emissions, production units, and carbon intensity.
- Highlight facilities with the highest carbon intensity.

### 4. Sustainability Target Performance
- Compare actual emissions against monthly emissions budgets or targets.
- Display target variance (%) for each facility.
- Identify facilities exceeding their emissions targets.
- Visualize emissions reduction progress wherever baseline data is available.

### 5. Interactive Filters
Include filters for:
- Facility
- City
- State
- Year
- Month

### 6. Dashboard Design
Use a clean, modern, executive-style layout with:
- White or light background.
- Subtle green accents representing sustainability.
- Clear KPI cards at the top.
- Interactive charts and tables organized into logical sections.
- Consistent units, labels, and formatting.

### Data Requirements
Use the available CarbonOps Gold-layer datasets, including:

- `carbonops.gold.facility_emissions`
- `carbonops.gold.carbon_intensity`
- `carbonops.gold.target_performance`
- `carbonops.gold.city_emissions`
- `carbonops.gold.state_emissions`
- `carbonops.gold.facility_performance`

Use existing Unity Catalog Metric Views where applicable.

Only reference columns and metrics that actually exist in the available datasets. Do not invent values, and avoid duplicating metrics across different visualizations.

**Goal:** Deliver an executive-ready sustainability dashboard that transforms CarbonOps manufacturing data into actionable insights for emissions monitoring, facility benchmarking, and sustainability decision-making.
```