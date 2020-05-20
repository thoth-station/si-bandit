#!/usr/bin/env python3
# si-bandit
# Copyright(C) 2020 Kevin Postlethwait.
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""This is the main script of the template project."""
from si_bandit.version import __version__ as si_bandit_version
import os
import subprocess
import tempfile
import tarfile
import click
import json
from typing import Optional
from thoth.common import init_logging
from bandit import __version__ as bandit_version
from pprint import PrettyPrinter
import datetime

pp = PrettyPrinter(indent=4)

init_logging()


@click.command()
@click.option(
    "--output",
    "-o",
    type=str,
    envvar="SI_BANDIT_OUTPUT",
    help="Output file to print results to.",
)
@click.option(
    "--from-directory",
    "-d",
    type=str,
    envvar="SI_BANDIT_DIR",
    help="Input directory for running bandit.",
)
@click.option(
    "--package-name",
    "-n",
    required=True,
    type=str,
    envvar="SI_BANDIT_PACKAGE_NAME",
    help="Name of package bandit is being run on.",
)
@click.option(
    "--package-version",
    type=str,
    envvar="SI_BANDIT_PACKAGE_VERSION",
    help="Version to be evaluated.",
)
@click.option(
    "--package-index",
    type=str,
    default="https://pypi.org/simple",
    envvar="SI_BANDIT_PACKAGE_INDEX",
    help="Which index is used to find package.",
)
def si_bandit(
    output: Optional[str],
    from_directory: Optional[str],
    package_name: str,
    package_version: Optional[str],
    package_index: Optional[str],
):
    """Run the cli for si-bandit."""
    if from_directory is None:
        d = tempfile.TemporaryDirectory()
        command = ["pip", "download", "--no-binary=:all:", "--no-deps", "-d", d.name, "-i", package_index]
        if package_version is not None:
            command.append(f"{package_name}=={package_version}")
        else:
            command.append(package_name)
        subprocess.run(command)
        for f in os.listdir(d.name):
            if f.endswith(".tar.gz"):
                full_path = os.path.join(d.name, f)
                tar = tarfile.open(full_path, "r:gz")
                tar.extractall(os.path.join(d.name, "package"))
                from_directory = os.path.join(d.name, "package")
                break

    with tempfile.NamedTemporaryFile() as f:
        print(f.name)
        subprocess.run(["bandit", "-r", "-f", "json", "-o", f.name, from_directory])
        with open(f.name, "r") as json_file:
            bandit_output = json.loads(json_file.read())

    out = dict()
    out["bandit_version"] = bandit_version
    out["si_bandit_version"] = si_bandit_version
    out["package_name"] = package_name
    out["time_stamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if package_version is None:
        out["package_version"] = "latest"
    else:
        out["package_version"] = package_version

    out["package_index"] = package_index

    out["bandit_output"] = bandit_output
    if output is not None:
        with open(output, 'w') as f:
            json.dump(out, f,)
    else:
        pp.pprint(out)


__name__ == "__main__" and si_bandit()
