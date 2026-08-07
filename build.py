import shlex
import shutil
import subprocess
import sys
from argparse import ArgumentParser
from pathlib import Path

PY = shlex.quote(sys.executable)

wheel_cmd = shlex.split(f"{PY} -m build -n -x --wheel --log build.log")
build_cmd = shlex.split(f"{PY} -m pip wheel . -v -w dist --log build.log")
install_cmd = shlex.split(f"{PY} -m pip install . -v --log build.log")
develop_cmd = shlex.split(f"{PY} setup.py develop")


def main(args=sys.argv[1:]):
    prog = ArgumentParser(prog="Build vonMises")
    prog.add_argument(
        "mode",
        help="""Build mode:
        wheel -- only builds the wheel
        develop -- creates an editable install
        install -- performs a normal install
        clean -- removes all build data""",
        type=str,
        choices=["wheel", "install", "develop", "clean"],
    )

    args = prog.parse_args(args)

    # Log to a file
    log_file = "build.log"

    def execute(command, log_file=log_file):
        subprocess.run(command, check=True)

    if args.mode == "wheel":
        print("Starting wheel build")
        execute(build_cmd)
        print("Wheel build completed")

    elif args.mode == "install":
        print("Starting install")
        execute(install_cmd)
        print("Finished installation")

    elif args.mode == "develop":
        print("Starting development build")
        execute(develop_cmd)
        print("Finished development build")

    elif args.mode == "clean":
        print("Starting cleanup")
        subprocess.run(shlex.split(f"{PY} -m pip uninstall vonMises -y"), check=True)
        subprocess.run(shlex.split("git clean -xdff"), cwd="src", check=True)

        for entry in Path("").iterdir():
            if entry.name in [
                "_skbuild",
                "dist",
                "build",
                ".pytest_cache",
            ] or entry.name.endswith("egg-info"):
                print(f"Removing '{entry}'")
                shutil.rmtree(entry)
            if entry.suffix == ".log":
                print(f"Removing '{entry}'")
                entry.unlink()
        print("Finished cleanup")


if __name__ == "__main__":
    main()
