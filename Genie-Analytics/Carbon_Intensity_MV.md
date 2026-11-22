## Create a Metric View for Carbon Intensity Calculations

Navigate to `Catalog`-> `carbonops`-> `gold`-> `Create`-> `Metric View`.

Select `carbonops.gold.carbon_intensity` as the source table and configure:

| Type | Name | Expression |
| :--- | :--- | :--- |
| Field | Facility | `source.facility_name` |
| Field | City | `source.city` |
| Field | Year | `source.year` |
| Measure | Total Emissions | `SUM(source.total_tco2e)` |
| Measure | Total Production | `SUM(source.production_units)` |
| Measure | Carbon Intensity | `SUM(source.total_tco2e) * 1000 / NULLIF(SUM(source.production_units), 0)` |

Save it as `carbonops.gold.carbon_intensity_metrics`.

### Test it out

Calculate overall carbon intensity
```sql
SELECT
    MEASURE(`Total Emissions`) AS total_emissions_tco2e,
    MEASURE(`Total Production`) AS total_production_units,
    ROUND(
        MEASURE(`Carbon Intensity`), 2
    ) AS carbon_intensity_kg_per_unit
FROM carbonops.gold.carbon_intensity_metrics;
```

Compare carbon intensity across facilities
```sql
SELECT
    `Facility`,
    ROUND(
        MEASURE(`Total Emissions`), 2
    ) AS total_emissions_tco2e,
    MEASURE(`Total Production`) AS production_units,
    ROUND(
        MEASURE(`Carbon Intensity`), 2
    ) AS carbon_intensity_kg_per_unit
FROM carbonops.gold.carbon_intensity_metrics
GROUP BY `Facility`
ORDER BY carbon_intensity_kg_per_unit DESC;
```