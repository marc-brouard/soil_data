import pytest
from unittest.mock import patch, MagicMock
from typing import List, Dict, Any, Optional
from app.main import (
    get_soil_data_between_points,
    create_soil_df,
    process_point,
    max_value,
    get_soil_linear_model,
)
import json
import pandas as pd


@pytest.fixture
def mock_requests_get():
    """patch requests.get

    Yields:
        _type_: returns the mock object
    """
    with patch("requests.get") as mock_get:
        yield mock_get


@pytest.fixture
def mock_response():
    """set up a mock response

    Returns:
        _type_: the mock response
    """
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {"mocked": "data"}
    return response


@pytest.fixture
def test_data() -> List[Dict[str, Any]]:
    """provides soil data for testing in the form of a list of dictionaries

    Returns:
        List[Dict[str, Any]]: the soil data as a list of dictionaries
    """
    with open("tests/data/soil_data.json") as f:
        return json.load(f)


@pytest.fixture
def test_point() -> Dict:
    """test data for one point

    Returns:
        Dict: the test data for one point
    """
    with open("tests/data/soil_point.json") as f:
        return json.load(f)


@pytest.fixture
def test_soil_df() -> pd.DataFrame:
    """creates a pandas dataframe of soil data for testing

    Returns:
        pd.DataFrame: the soil data as a pandas dataframe
    """
    with open("tests/data/soil_data.csv") as f:
        return pd.read_csv(f)


@pytest.fixture
def test_soil_model_summary() -> str:
    """the results of the linear model summary for the soil data as text

    Returns:
        str: the summary of the linear model for the soil data
    """
    with open("tests/data/soil_model_summary.txt") as f:
        return f.read()


def test_get_soil_data_between_points(mock_requests_get, mock_response):
    """test the get_soil_data_between_points function

    Args:
        mock_requests_get (_type_): mocked requests.get
        mock_response (_type_): mocked response
    """
    mock_requests_get.return_value = mock_response

    # Call the function under test
    soil_data = get_soil_data_between_points(
        56.225297, 8.662215, 55.958103, 9.354390, num_points=3
    )

    # Assert that requests.get was called the expected number of times with the correct arguments
    assert mock_requests_get.call_count == 3
    # Assert that the call to requests.get was called with the correct arguments
    assert (
        mock_requests_get.call_args.args[0]
        == "https://rest.isric.org/soilgrids/v2.0/properties/query"
    )
    # Assert that the call to requests.get was called with the correct property value
    assert mock_requests_get.call_args.kwargs["params"]["property"] == [
        "clay",
        "sand",
        "silt",
        "ocs",
    ]
    assert mock_requests_get.call_args.kwargs["params"]["depth"] == [
        "0-30cm",
        "0-5cm",
        "5-15cm",
        "15-30cm",
    ]
    assert mock_requests_get.call_args.kwargs["params"]["value"] == "mean"

    # Assert the result of the function under test
    assert soil_data == [{"mocked": "data"}, {"mocked": "data"}, {"mocked": "data"}]


def test_create_soil_df(test_data: List[Dict[str, Any]]):
    """test the creation of a pandas dataframe from the soil data

    Args:
        test_data (List[Dict[str, Any]]): the soil data to create the dataframe from
    """
    soil_df: pd.DataFrame = create_soil_df(test_data)

    # check the shape of the dataframe
    assert soil_df.shape == (5, 4)
    # check the first 3 rows of the dataframe
    assert soil_df.columns.tolist() == ["clay", "sand", "silt", "ocs"]
    assert soil_df.iloc[0].tolist() == [86, 787, 134, 63]
    assert soil_df.iloc[1].tolist() == [75, 833, 120, 66]
    assert soil_df.iloc[2].tolist() == [87, 840, 96, 61]


def test_process_point(test_point: Dict):
    """test the processing of a single point

    Args:
        test_point (Dict): the point data to process
    """
    soil_point = process_point(test_point)

    # check that a list is returned
    assert isinstance(soil_point, list)
    # check that the list has the correct length and values
    assert len(soil_point) == 4
    assert soil_point == [86, 787, 134, 63]


def test_max_value(test_point: Dict):
    """test the max_value function

    Args:
        test_point (Dict): the point data to get the maximum values from
    """
    max_clay_value: Optional[float] = max_value(test_point, "clay")
    max_sand_value: Optional[float] = max_value(test_point, "sand")
    max_silt_value: Optional[float] = max_value(test_point, "silt")
    max_ocs_value: Optional[float] = max_value(test_point, "ocs")

    # check that the correct values are returned
    assert max_clay_value == 86
    assert max_sand_value == 787
    assert max_silt_value == 134
    assert max_ocs_value == 63


def test_get_soil_linear_model(
    test_soil_df: pd.DataFrame, test_soil_model_summary: str
):
    """test the running of the R model and the returned summary

    Args:
        test_soil_df (pd.DataFrame): the pandas dataframe of soil data
        test_soil_model_summary (str): as string to compare the summary to
    """
    soil_model = get_soil_linear_model(test_soil_df)

    # check that the summary is correct
    assert str(soil_model).strip("\n") == test_soil_model_summary.strip("\n")
