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
from thoth.si_bandit.version import __version__ as si_bandit_version
from thoth.si_bandit.version import __title__ as si_bandit_title
import os
import tempfile
import tarfile
import click
from typing import Optional
from typing import Dict
from typing import Any

from thoth.analyzer import run_command
from thoth.analyzer import print_command_result
from thoth.common import init_logging

from thoth.python import Source

init_logging()


def _run_bandit(from_directory: str) -> Optional[Dict[str, Any]]:
    results = run_command(f"bandit -r -f json {from_directory}", is_json=True, raise_on_error=False)
    out = results.stdout
    if out is None:
        raise Exception(results.stderr)
    if out["errors"] != []:
        raise Exception(out["errors"])
    return out


@click.command()
@click.pass_context
@click.option(
    "--output", "-o", type=str, default="-", envvar="THOTH_SI_BANDIT_OUTPUT", help="Output file to print results to."
)
@click.option(
    "--from-directory", "-d", type=str, envvar="THOTH_SI_BANDIT_DIR", help="Input directory for running bandit."
)
@click.option(
    "--package-name",
    "-n",
    required=True,
    type=str,
    envvar="THOTH_SI_BANDIT_PACKAGE_NAME",
    help="Name of package bandit is being run on.",
)
@click.option(
    "--package-version",
    type=str,
    required=True,
    envvar="THOTH_SI_BANDIT_PACKAGE_VERSION",
    help="Version to be evaluated.",
)
@click.option(
    "--package-index",
    type=str,
    default="https://pypi.org/simple",
    envvar="THOTH_SI_BANDIT_PACKAGE_INDEX",
    help="Which index is used to find package.",
)
@click.option("--no-pretty", is_flag=True, help="Do not print results nicely.")
def si_bandit(
    click_ctx,
    output: Optional[str],
    from_directory: Optional[str],
    package_name: str,
    package_version: Optional[str],
    package_index: Optional[str],
    no_pretty: bool,
):
    """Run the cli for si-bandit."""
    if from_directory is None:
        with tempfile.TemporaryDirectory() as d:
            command = (
                f"pip download --no-binary=:all: --no-deps -d {d} -i {package_index} "
                f"{package_name}==={package_version}"
            )
            run_command(command)
            for f in os.listdir(d):
                if f.endswith(".tar.gz"):
                    full_path = os.path.join(d, f)
                    tar = tarfile.open(full_path, "r:gz")
                    tar.extractall(os.path.join(d, "package"))
                    from_directory = os.path.join(d, "package")
                    break
            else:
                raise FileNotFoundError(
                    f"No source distribution found for {package_name}==={package_version} " f"on {package_index}"
                )
            out = _run_bandit(from_directory)
    else:
        out = _run_bandit(from_directory)

    if out is None:
        raise RuntimeError("output of bandit is empty")

    source_dict = {"url": package_index, "name": "foo", "verify_ssl": False, "warehouse": True}
    source = Source.from_dict(source_dict)

    try:
        out["time_of_release"] = source.get_package_release_date(
            package_name=package_name, package_version=package_version
        )
    except Exception:
        out["time_of_release"] = None

    print_command_result(
        click_ctx=click_ctx,
        result=out,
        analyzer=si_bandit_title,
        analyzer_version=si_bandit_version,
        output=output,
        duration=None,
        pretty=not no_pretty,
    )


__name__ == "__main__" and si_bandit()
