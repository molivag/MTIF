import argparse

def main():

    parser = argparse.ArgumentParser(prog="mtif")

    sub = parser.add_subparsers(dest="command")

    sub.add_parser("upload")
    sub.add_parser("download")
    sub.add_parser("mesh")

    args = parser.parse_args()

    if args.command == "upload":
        print("uploading...")

    elif args.command == "download":
        print("downloading...")
