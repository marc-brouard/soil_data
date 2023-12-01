# Soil point data from rest.isric.org

This program retrieves a specified number of point soil data from rest.isric.org, calculates the max value for the specified properties across the specified depths and uses this data to run a simple linear model.

## Building

A dockerfile is provided, use the following command to build the docker container

```
docker build . -t soil_data
```

and to run the docker container

```
docker run soil_data
```

## Expected output

The output from running the program will report each point downloaded and once all the points have been downloaded, the summary of the linear model will be printed to the terminal.

## Development build

For development purposes a development version of the requirements is provided. A make file is provided with shortcuts. To make the development environment use the following commands.

```
make clean 
make init
make install-dev
```

You can then activate the python environment using

```
source .venv/bin/activate
```

## Additional tools

The development environment has a number of tools installed to lint and format the code.

| Command | Description |
|---------|-------------|
| make mypy | mypy type checks the code |
| make lint | runs `ruff` to lint the code |
| make fmt | runs `ruff` as a formatter, to format the code to standard |
| make test | runs `pytest`, which runs the tests in the `tests` directory |