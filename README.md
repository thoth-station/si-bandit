# si-bandit

This file creates a bandit document to be used as a security indicator.

It can be run one of two ways, either a directory is provided where the package is already downloaded and extracted or
`pip download` is used to download the source.

To checkout result for particular package in local -
1. `pipenv install --dev`
2. `pipenv run python3 si-bandit --help`
3. `pipenv run python3 si-bandit --package-name <package-name> --package-version <version> --output result`

After downloading the tar and extracting the package you can run -
 - `pipenv run python3 si-bandit -d <path> --package-name <package-name> --package-version <version> --output result`
