import sys
import argparse
import json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Specify a .json file containing at least the keys 'postgres-port' and"
                                                 " 'postgres-dir' holding the respective information and pass this file"
                                                 " as an argument to this script. It will output a shell script to run"
                                                 " a docker container from an image called dionysos-volante:alpha.")
    parser.add_argument("credentials", help="path to .json file holding the credentials with the minimum needed keys"
                                            " 'postgres-user' and 'postgres-password'.")
    parser.add_argument("-o", "--output", help="optional output path of created shell script")
    return parser.parse_args()


def parse_credentials(credentials_path: str) -> dict:
    """ returns parsed credentials from given path, returns empty dictionary if required keys are missing
    :param str credentials_path: path to credentials
    :return: dictionary with keys at least keys "postgres-port", and "postgres-dir" with respective values, if all keys
        are given, otherwise it returns an empty dictionary
    :rtype: dict
    """
    with open(credentials_path, "r") as f:
        credentials = json.load(f)

    returning_credentials = credentials

    required_keys = ["postgres-port", "postgres-dir"]
    for required_key in required_keys:
        if required_key not in credentials:
            returning_credentials = dict()

    return returning_credentials


def create_shell_script(credentials: dict, output_path: str) -> None:
    """ creates shell script for starting dionysos-volante image (PostgresSQL) with correct port and volume binding
    :param dict credentials: dictionary containing at least the keys "postgres-port", "postgres-dir" and respective
        values
    :param str output_path: path to shell script which should be written into, e.g. ./start_db.sh; Nb. needs the file
        ending ".sh"!
    """
    with open(output_path, "w") as f:
        port = credentials["postgres-port"]
        saving_dir = credentials["postgres-dir"]
        f.writelines([f"docker run -d -i --rm -p {port}:5432 -v {saving_dir}:/var/lib/postgresql/data dionysos-volante:alpha"])


def main() -> None:
    args = parse_args()
    credentials = parse_credentials(credentials_path=args.credentials)

    if not credentials:
        sys.exit("Invalid JSON file! The JSON file did not contain the keys 'postgres-port', and 'postgres-dir'")

    output_path = "./database_config/start_database.sh"

    if args.output:
        output_path = args.output

    create_shell_script(credentials=credentials, output_path=output_path)


if __name__ == '__main__':
    main()
