import subprocess

import mkdocs_gen_files


output = subprocess.check_output(
    "typer tinymotion_backend.cli utils docs --name tinymotion-backend",
    shell=True,
    universal_newlines=True,
)

with mkdocs_gen_files.open("CLI/cli.md", "w") as f:
    f.write(output)
