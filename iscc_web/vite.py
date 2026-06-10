import json
import pathlib
from urllib.parse import urljoin
from jinja2_simple_tags import StandaloneTag
from markupsafe import Markup
from typing import Optional
from iscc_web.options import opts


PROJECT_DIR = pathlib.Path(__file__).parent.parent

VITE_DEV_MODE = opts.environment == "development"
VITE_STATIC_URL = "/static/dist/"
VITE_MANIFEST_PATH = PROJECT_DIR / "iscc_web" / "static" / "dist" / "manifest.json"


def load_manifest(path: pathlib.Path = VITE_MANIFEST_PATH) -> dict:
    """Load the Vite build manifest from `path` or raise RuntimeError if it does not exist."""
    if path.exists():
        with open(path, "r") as f:
            return json.load(f)
    raise RuntimeError("Could not find Vite manifest.json at " + str(path))


VITE_MANIFEST: Optional[dict] = None if VITE_DEV_MODE else load_manifest()


class ViteHmrClientExtension(StandaloneTag):
    tags = {"vite_hmr_client"}

    def render(self):
        if not VITE_DEV_MODE:
            return ""
        return generate_script_tag("http://localhost:5173/@vite/client")


class ViteAssetExtension(StandaloneTag):
    tags = {"vite_asset"}

    def render(self, asset_path):
        if VITE_DEV_MODE:
            return generate_script_tag(f"http://localhost:5173/{asset_path}")

        if not VITE_MANIFEST or asset_path not in VITE_MANIFEST:
            raise RuntimeError(f"Cannot find {asset_path} in manifest at {VITE_MANIFEST_PATH}")

        manifest_entry = VITE_MANIFEST[asset_path]
        generated_tags = []

        generated_tags.extend(self.__generate_css_tags(asset_path))

        generated_tags.append(generate_script_tag(urljoin(VITE_STATIC_URL, manifest_entry["file"])))

        # str.join returns a plain str even for Markup items, which Jinja would autoescape
        return Markup("\n".join(generated_tags))

    def __generate_css_tags(self, asset_path: str, seen_tags=None):
        if not VITE_MANIFEST or asset_path not in VITE_MANIFEST:
            raise RuntimeError(f"Cannot find {asset_path} in manifest at {VITE_MANIFEST_PATH}")

        if seen_tags is None:
            seen_tags = set()

        manifest_entry = VITE_MANIFEST[asset_path]
        generated_tags = []

        if "imports" in manifest_entry:
            for import_path in manifest_entry["imports"]:
                generated_tags.extend(self.__generate_css_tags(import_path, seen_tags))

        if "css" in manifest_entry:
            for css_path in manifest_entry["css"]:
                tag = generate_stylesheet_tag(urljoin(VITE_STATIC_URL, css_path))

                if tag not in seen_tags:
                    generated_tags.append(tag)
                    seen_tags.add(tag)

        return generated_tags


def register_extensions(jinja_env):
    """Register Vite Jinja2 extensions on the given Jinja2 Environment."""
    jinja_env.add_extension(ViteHmrClientExtension)
    jinja_env.add_extension(ViteAssetExtension)


def generate_script_tag(src):
    return Markup(f'<script type="module" crossorigin="" src="{src}"></script>')


def generate_stylesheet_tag(href):
    return Markup(f'<link rel="stylesheet" href="{href}" />')
