# -*- coding: utf-8 -*-
import pathlib
import yaml


HERE = pathlib.Path(__file__).parent.absolute()


def reformat():
    for f in HERE.parent.glob("**\*.yaml"):
        with open(f, "rt", encoding="utf-8") as infile:
            data = yaml.safe_load(infile)
        with open(f, "wt", encoding="utf-8", newline="\n") as outf:
            yaml.safe_dump(
                data,
                outf,
                indent=2,
                width=88,
                encoding="utf-8",
                sort_keys=False,
                default_flow_style=False,
                default_style=None,
                allow_unicode=True,
            )


if __name__ == "__main__":
    reformat()
