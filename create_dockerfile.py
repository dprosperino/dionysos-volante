# As today, according to the official documentation https://docs.docker.com/engine/reference/commandline/secret_create/
# https://docs.docker.com/engine/swarm/secrets/ (both 2021-04-25) and other resources
# https://serverfault.com/questions/871090/how-to-use-docker-secrets-without-a-swarm-cluster (2021-04-25), it is not
# possible to use docker secrets with only containers. Instead, docker swarms or docker compose functionality is
# required. However, docker compose does not work on the RaspberryPi, probably due to missing binaries (there are no
# ARM64 binaries listed on the official binaries site https://dl.bintray.com/docker-compose/master/ (2021-04-25)).
#
# So, the hacky work-around is to store the credentials classically in a .json file, which is not tracked by git, and
# then use this python script to read the credentials and write them into the Dockerfile.

import sys
import argparse
import json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Specify a .json file containing the keys 'postgres-user' and"
                                                 " 'postgres-password' holding the respective information and pass this"
                                                 " file as an argument to this script. It will output a Dockerfile"
                                                 " ready to build a postgres:13 image with specified credentials.",
                                     epilog="Docker secrets is only available for swarm execution and docker compose."
                                            " Neither of those is available for the RaspberryPi, so in order to prevent"
                                            " the credentials for being tracked on version control, this script is"
                                            " saved instead of the Dockerfile.")
    parser.add_argument("credentials", help="path to .json file holding the credentials with the keys 'postgres-user'"
                                            " and 'postgres-password'.")
    parser.add_argument("-o", "--output", help="optional output path of created Dockerfile", action="store_true")
    return parser.parse_args()


def parse_credentials(credentials_path: str) -> dict:
    """ returns parsed credentials from given path, returns empty dictionary if required keys are missing

    :param str credentials_path: path to credentials
    :return: dictionary with keys "postgres-user", "postgres-password", "postgres-port", and "postgres-dir" with
        respective values, if all four keys are given, otherwise it returns an empty dictionary
    :rtype: dict
    """
    with open(credentials_path, "r") as f:
        credentials = json.load(f)

    returning_credentials = credentials

    required_keys = ["postgres-user", "postgres-password", "postgres-port", "postgres-dir"]
    for required_key in required_keys:
        if required_key not in credentials:
            returning_credentials = dict()

    return returning_credentials


def create_dockerfile(credentials: dict, output_path: str) -> None:
    """ creates Dockerfile for PostgreSQL 13 database with initial user and password and exposes given port

    :param dict credentials: dictionary containing "postgres-user", "postgres-password", "postgres-port", "postgres-dir"
        and respective values
    :param str output_path: path to Dockerfile which should be written into, e.g. ./Dockerfile; Nb. needs the Dockerfile
        ending!
    """
    with open(output_path, "w") as f:
        f.writelines(["FROM postgres:13", "\n", "\n",
                      f"ENV POSTGRES_USER={credentials['postgres-user']}", "\n",
                      f"ENV POSTGRES_PASSWORD={credentials['postgres-password']}", "\n",
                      f"ENV POSTGRES_DB=dionysos", "\n", "\n",
                      f"EXPOSE {credentials['postgres-port']}"])


def main() -> None:
    args = parse_args()
    credentials = parse_credentials(credentials_path=args.credentials)

    if not credentials:
        sys.exit("Invalid JSON file! The JSON file did not contain the keys 'postgres-user', 'postgres-password',"
                 " 'postgres-port', and 'postgres-dir'")

    output_path = "./Dockerfile"
    if args.output:
        output_path = args.output

    create_dockerfile(credentials=credentials, output_path=output_path)


if __name__ == '__main__':
    main()
