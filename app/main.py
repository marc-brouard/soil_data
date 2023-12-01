from typing import List, Dict, Any, Optional
import requests
import pandas as pd
from rpy2.robjects import r, pandas2ri
from rpy2.robjects.packages import importr


def get_soil_data_between_points(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    num_points: int = 50,
) -> List[Dict[str, Any]]:
    """Retrieve soil data between two points

    Args:
        start_lat (float): the latitude of the starting point
        start_lon (float): the longitude of the starting point
        end_lat (float): the latitude of the ending point
        end_lon (float): the longitude of the ending point
        num_points (int, optional): the number of points to retrieve. Defaults to 5.

    Returns:
        List[Dict[str, Any]]: _description_
    """
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

    print("Attempting to fetch data between the specified points")

    # Iterate through the generated points and retrieve soil data for each point
    for lat, lon in zip(lats, lons):
        # create the payload for the request
        payload = {
            "lon": lon,
            "lat": lat,
            "property": ["clay", "sand", "silt", "ocs"],
            "depth": ["0-30cm", "0-5cm", "5-15cm", "15-30cm"],
            "value": "mean",
        }

        # Make a request to the SoilGrids API
        url = "https://rest.isric.org/soilgrids/v2.0/properties/query"
        response = requests.get(url, params=payload)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Append the soil data to the list
            print(f"Successfully fetched data for point ({lat}, {lon})")
            soil_data.append(response.json())
        else:
            # Print an error message if the request was not successful
            print(
                f"Error fetching data for point ({lat}, {lon}). Status code: {response.status_code}"
            )

    return soil_data


def max_value(point: Dict, property_name: str) -> Optional[float]:
    """gets the maximum value for a property

    Args:
        point (Dict): the data for a point
        property_name (str): the name of the property to get the maximum value for

    Returns:
        Optional[float]: the maximum value for the property
    """
    property_data = next(
        (
            layer
            for layer in point["properties"]["layers"]
            if layer["name"] == property_name
        ),
        None,
    )
    if property_data:
        mean_values = [depth["values"]["mean"] for depth in property_data["depths"]]
        return max(mean_values)
    else:
        return None


def process_point(point: Dict) -> List:
    """Process the data for a point getting the maximum values for each property

    Args:
        point (Dict): the point data to process

    Returns:
        List: a list of the maximum values for each property
    """
    clay_values: Optional[float] = max_value(point, "clay")
    sand_values: Optional[float] = max_value(point, "sand")
    silt_values: Optional[float] = max_value(point, "silt")
    ocs_values: Optional[float] = max_value(point, "ocs")

    return [clay_values, sand_values, silt_values, ocs_values]


def create_soil_df(soil_data: List) -> pd.DataFrame:
    """create a pandas dataframe from the soil data

    Args:
        soil_data (List): the soil data to create the dataframe from

    Returns:
        pd.DataFrame: the created dataframe
    """
    soil_values = [process_point(point) for point in soil_data]

    return pd.DataFrame(soil_values, columns=["clay", "sand", "silt", "ocs"])


def get_soil_linear_model(soil_data: pd.DataFrame) -> str:
    """given a dataframe of soil data, create a linear model by calling to R

    Args:
        soil_data (pd.DataFrame): the pandas dataframe of soil data

    Returns:
        str: the result of the linear model
    """
    pandas2ri.activate()
    r_soil_df = pandas2ri.py2rpy(soil_data)

    # we need to import the required R packages
    base = importr("base")

    # source the r script
    base.source("app/linear_model.r")

    result = r.soil_model(r_soil_df)

    return pandas2ri.rpy2py(result)


def main():
    start_lat: float = 56.225297
    start_lon: float = 8.662215
    end_lat: float = 55.958103
    end_lon: float = 9.354390
    num_points: float = 5

    soil_data: List = get_soil_data_between_points(
        start_lat, start_lon, end_lat, end_lon, num_points
    )

    soil_df = create_soil_df(soil_data)

    stats = get_soil_linear_model(soil_df)

    print(stats)


if __name__ == "__main__":
    main()
