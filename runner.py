#!/usr/bin/env python3
import os
from pathlib import Path
import subprocess
import typing


# TODO: add support for L10n
# TODO: create better parser to distinguish sections
# TODO: add support for desktop actions
# TODO: add support for *.direcory files


terminal_exec: list[str] = [
    "kitty",
]


runner_exec: tuple[str, ...] = (
    "bemenu",
    "-i",
)

# TODO: use $XDG_DATA_DIRS instead
entries_directories: tuple[Path, ...] = (
    Path("/usr/share/applications"),
    Path("/usr/local/share/applications"),
    Path(os.getenv("XDG_DATA_HOME") or "~/.local/share") / "applications",
)


apps: dict[str, list[str]] = {}


def parse_entry(entry_path: Path) -> None:
    name: typing.Optional[str] = None
    exec: list[str] = []
    with open(entry_path, "r", encoding="utf-8") as f:
        for line in f:
            match line.split("=", 1):
                case [header]:
                    # Usually desktop entry section goes first, so we won't
                    # sacrifice on correctness much
                    if header != "[Desktop Entry]\n":
                        return
                
                case ["Name", s]:
                    name = s
                
                case ["Hidden" | "NoDisplay", s]:
                    # Don't need to even list this entries
                    # https://specifications.freedesktop.org/desktop-entry-spec/latest/ar01s06.html
                    if s == "true\n":
                        return
                
                case ["Exec", s]:
                    exec += s.rstrip().split()
                
                case ["Terminal", s]:
                    if s == "true\n":
                        exec = terminal_exec + exec
    if name is None:
        return

    apps[name] = exec


def main() -> None:
    for d in entries_directories:
        for entry_path in d.glob("*.desktop"):
            parse_entry(entry_path)

    try:
        chosen_app_name = subprocess.check_output(
            runner_exec,
            encoding="utf-8",
            input="".join(apps.keys())
        )
    except Exception:
        exit(1)

    subprocess.run(
        [arg for arg in apps[chosen_app_name]
         if len(arg) != 2 and not arg.startswith("%")]
        # Don't handle field codes
        # https://specifications.freedesktop.org/desktop-entry-spec/latest/ar01s07.html
    )


if __name__ == "__main__":
    main()
