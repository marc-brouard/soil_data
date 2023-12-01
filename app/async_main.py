import httpx
import pandas as pd
import asyncio
from tenacity import AsyncRetrying, stop_after_attempt, wait_fixed
import logging

logging.basicConfig(
    format="%(levelname)s [%(asctime)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
)


async def get_soil_data(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    num_points: int,
    max_connections=5,
    timeout=10,
):
    api_url = "https://rest.isric.org/soilgrids/v2.0/properties/query"

    # this will create a list of evenly spaced latitudes and longitudes (a transect)
    # rounded to 6 decimal places
    lats = [
        round(start_lat + i * (end_lat - start_lat) / (num_points - 1), 6)
        for i in range(num_points)
    ]
    lons = [
        round(start_lon + i * (end_lon - start_lon) / (num_points - 1), 6)
        for i in range(num_points)
    ]

    # Create a list to store soil data for each point
    soil_data: List[Dict[str, Any]] = []

    async with httpx.AsyncClient(
        limits=httpx.Limits(max_connections=max_connections)
    ) as client:
        tasks = []

        for lat, lon in zip(lats, lons):
            payload = {
                "lon": lon,
                "lat": lat,
                "property": ["clay", "sand", "silt", "ocs"],
                "depth": ["0-30cm", "0-5cm", "5-15cm", "15-30cm"],
                "value": "mean",
            }

            # Wrap the client.get call with tenacity's AsyncRetrying
            async def fetch_data():
                return await client.get(api_url, params=payload, timeout=timeout)

            retrying = AsyncRetrying(stop=stop_after_attempt(3), wait=wait_fixed(2))
            tasks.append(retrying(fetch_data))

        responses = await asyncio.gather(*tasks)

        for response, lat, lon in zip(responses, latitudes, longitudes):
            if response.status_code == 200:
                data = response.json()
                soil_data.append(data)
            else:
                print(
                    f"Error {response.status_code} for coordinates ({lat}, {lon}): {response.text}"
                )

    return soil_data


def main():
    start_lat: float = 56.225297
    start_lon: float = 8.662215
    end_lat: float = 55.958103
    end_lon: float = 9.354390
    num_points: float = 50

    # Run the event loop to execute the asynchronous function
    soil_data: List[Dict[str, Any]] = asyncio.run(
        get_soil_data(start_lat, start_lon, end_lat, end_lon, num_points)
    )

    print(soil_data)


if __name__ == "__main__":
    main()
