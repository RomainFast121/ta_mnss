#!/usr/bin/env python

import argparse
import os
import shutil
import subprocess

parser = argparse.ArgumentParser(
    description="Small tool to publish notebooks for classes"
)

parser.add_argument(
    "--solution", action="store_true", help="requires to include the solution"
)

parser.add_argument("input_directory", type=str, help="directory to publish")

parser.add_argument(
    "--output",
    "-o",
    type=str,
    help="directory where to publish the result",
    default="./publish",
)

parser.add_argument(
    "--keep_metadata", "-k", action="store_true", help="request to keep cell metadata"
)


args = parser.parse_args()
print(args)

# make the output directory
try:
    os.mkdir(args.output)
except FileExistsError:
    pass

target_dir = os.path.join(args.output, args.input_directory)
# clean target
try:
    shutil.rmtree(target_dir)
except FileNotFoundError:
    pass

# copy the directoy content
shutil.copytree(
    args.input_directory,
    target_dir,
    ignore=shutil.ignore_patterns("*.tex"),
    symlinks=True,
    dirs_exist_ok=True,
)


def __run(command):
    print(command)
    ret = subprocess.run(command, shell=True)
    if ret.returncode:
        raise RuntimeError("could not run: " + command)


# loops over the note books
os.chdir(target_dir)
for f in os.listdir():
    if not os.path.isfile(f):
        continue
    ext = os.path.splitext(f)[1]
    if not ext == ".ipynb":
        continue

    os.rename(f, "tmp.ipynb")
    # removes the solution
    __run(f"slides -f tmp.ipynb -o {f}")
    if args.keep_metadata:
        __run(
            "nb-clean clean --preserve-cell-metadata "
            f"tags slideshow cell_style hide_input -- {f}"
        )
    else:
        __run(f"nb-clean clean {f}")

    # removes the solution and test execution
    if args.solution:
        solution_name = os.path.splitext(f)[0] + "_solution.ipynb"
        __run(f"slides -p tmp.ipynb -o {solution_name}")
        __run(f"slides {solution_name} --html")

        # runs the notebooks
        __run(
            f"jupyter nbconvert --to notebook --execute {solution_name} --output tmp.ipynb"
        )

        if args.keep_metadata:
            __run(
                "nb-clean clean --preserve-cell-metadata "
                f"tags slideshow cell_style hide_input -- {solution_name}"
            )
        else:
            __run(f"nb-clean clean {solution_name}")

        try:
            os.unlink("talk.ipynb")
            os.unlink("talk.slides.html")
        except FileNotFoundError:
            pass

    os.unlink("tmp.ipynb")
