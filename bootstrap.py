"""
Delve Bootstrap Script
Modular, testable, and focused on the current platform only.
"""
import sys
import os
import re
import shlex
import shutil
import subprocess
import logging
import argparse
import pathlib
import hashlib
from typing import List, Optional, Sequence, Tuple

from delve import __version__ as DELVE_VERSION

__here__ = pathlib.Path(__file__).parent.resolve()


# --- Utility Functions ---
def setup_logging(log_level, log_file=None):
    """
    Set up logging to both stdout and a file.
    If log_file is None, defaults to 'bootstrap.log' in the script directory.
    """
    log_file = log_file or (__here__ / "bootstrap.log")
    log_level_value = getattr(logging, log_level)
    formatter = logging.Formatter("%(levelname)s: %(name)s: %(process)d: %(threadName)s: %(module)s: %(pathname)s: %(funcName)s: %(lineno)d: %(asctime)s: %(message)s")

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level_value)

    # StreamHandler (stdout)
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(log_level_value)
    sh.setFormatter(formatter)
    root_logger.addHandler(sh)

    # FileHandler
    fh = logging.FileHandler(log_file, mode="a")
    fh.setLevel(log_level_value)
    fh.setFormatter(formatter)
    root_logger.addHandler(fh)

def get_platform():
    if sys.platform.startswith('linux'):
        return 'linux', 'unknown-linux-gnu'
    elif sys.platform.startswith('win'):
        return 'windows', 'windows-msvc'
    elif sys.platform.startswith('darwin'):
        return 'darwin', 'apple-darwin'
    else:
        raise RuntimeError(f"Unsupported platform: {sys.platform}")

def rglob_patterns(base: pathlib.Path, patterns: List[str]):
    for pattern in patterns:
        yield from base.rglob(pattern)

def get_file_sha256(p):
    sha256 = hashlib.sha256()
    with open(p, 'rb') as fp:
        while True:
            data = fp.read(65536)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()


def parse_cpython_asset_version(asset_name: str) -> Optional[Tuple[int, int, int]]:
    """Return a stable CPython version tuple from an asset name.

    Pre-release assets such as alpha, beta, and release candidate builds are
    rejected by returning ``None``.
    """
    match = re.search(
        r'cpython-(?P<version>\d+\.\d+\.\d+)(?P<suffix>[A-Za-z]+\d+)?(?=[^0-9A-Za-z]|$)',
        asset_name,
    )
    if not match or match.group('suffix'):
        return None
    return tuple(int(part) for part in match.group('version').split('.'))


def select_python_release_asset(
    release_names: Sequence[str],
    platform_tag: str,
    architecture: str = 'x86_64',
) -> Optional[str]:
    """Select the newest stable standalone CPython asset for a platform."""
    matching_assets = [
        name for name in release_names
        if 'install_only_stripped' in name
        and platform_tag in name
        and architecture in name
    ]
    stable_assets = [
        (name, version)
        for name in matching_assets
        for version in [parse_cpython_asset_version(name)]
        if version is not None
    ]
    stable_assets.sort(key=lambda item: item[1], reverse=True)
    if not stable_assets:
        return None
    return stable_assets[0][0]

# --- Subcommand Implementations ---
def clean(args):
    """Clean up build artifacts and other specified files/directories."""
    patterns = []
    if args.all or not any([args.node, args.python, args.static, args.extra]):
        patterns = [
            "build",
            "dist",
            "staticfiles",
            "__pycache__",
            "*.log",
            "build.log",
            "node_modules",
            "package-lock.json"
        ]
    else:
        if args.node:
            patterns += ["node_modules", "package-lock.json"]
        if args.python:
            patterns += ["build", "dist", "__pycache__", "*.log", "build.log"]
        if args.static:
            patterns += ["staticfiles"]
        if args.extra:
            patterns += args.extra
    logging.info(f"Cleaning patterns: {patterns}")
    for match in rglob_patterns(args.path, patterns):
        if match.name == "bootstrap.log":
            continue
        if args.dry_run:
            logging.info(f"Dry run: Would remove {match}")
        else:
            if match.is_file():
                logging.info(f"Removing file: {match}")
                match.unlink()
            elif match.is_dir():
                logging.info(f"Removing directory: {match}")
                shutil.rmtree(match, ignore_errors=True)


def download_python(args):
    """Download the latest non-rc Python standalone for the current platform."""

    plat, plat_str = get_platform()
    target_dir = args.target_dir.resolve()
    target_dir.mkdir(parents=True, exist_ok=True)
    if args.dry_run:
        logging.info(
            "Dry run: Would download the latest stable Python standalone "
            f"release and SHA256SUMS to {target_dir}"
        )
        return

    import requests

    latest_release_url = "https://raw.githubusercontent.com/astral-sh/python-build-standalone/latest-release/latest-release.json"
    logging.debug(f"Fetching latest release tag from: {latest_release_url}")
    tag = requests.get(latest_release_url).json()["tag"]
    logging.debug(f"Latest release tag: {tag}")
    github_api_url = f"https://api.github.com/repos/astral-sh/python-build-standalone/releases/tags/{tag}"
    logging.debug(f"Fetching release assets from: {github_api_url}")
    headers = {
        'X-GitHub-Api-Version': '2022-11-28',
        'Accept': 'application/vnd.github+json'
    }
    assets = requests.get(github_api_url, headers=headers).json()["assets"]
    release_names = [a["name"] for a in assets]
    logging.debug(f"Release asset names: {release_names}")
    release_file = select_python_release_asset(release_names, plat_str)
    logging.debug(f"Selected stable release asset: {release_file}")
    if not release_file:
        logging.error(f"No suitable release found for platform: {plat}")
        sys.exit(1)
    hash_file = "SHA256SUMS"
    def asset_url(name):
        for a in assets:
            if a["name"] == name:
                return a["url"]
        return None
    hash_file_url = asset_url(hash_file)
    release_file_url = asset_url(release_file)
    logging.debug(f"Release file URL: {release_file_url}")
    logging.debug(f"Hash file URL: {hash_file_url}")
    asset_headers = {
        'X-GitHub-Api-Version': '2022-11-28',
        'Accept': 'application/octet-stream'
    }
    hash_file_path = target_dir.joinpath(hash_file)
    release_file_path = target_dir.joinpath(release_file)
    logging.debug(f"Local hash file path: {hash_file_path}")
    logging.debug(f"Local release file path: {release_file_path}")
    with open(hash_file_path, "wb") as fp:
        fp.write(requests.get(hash_file_url, headers=asset_headers).content)
    with open(release_file_path, "wb") as fp:
        fp.write(requests.get(release_file_url, headers=asset_headers).content)
    logging.info(f"Downloaded {release_file} and {hash_file} to {target_dir}")

    # Checksum verification

    hash_hex = None
    for line in hash_file_path.read_text().splitlines():
        if release_file in line:
            hash_hex = line.split()[0]
            break
    if not hash_hex:
        logging.error(f"Could not find hash for {release_file} in {hash_file}")
        sys.exit(1)
    actual_hash = get_file_sha256(release_file_path)
    logging.debug(f"Expected hash: {hash_hex}")
    logging.debug(f"Actual hash:   {actual_hash}")
    if hash_hex != actual_hash:
        logging.error(f"Checksum mismatch for {release_file}: expected {hash_hex}, got {actual_hash}")
        sys.exit(1)
    logging.info(f"Checksum verified for {release_file}")


def extract_python(args):
    """Extract the downloaded Python archive to the assemble directory."""
    plat, _ = get_platform()
    logging.info(f"Extracting Python for platform: {plat}")
    downloads_dir = args.downloads_dir.resolve()
    logging.debug(f"Downloads directory: {downloads_dir}")
    assemble_dir = args.assemble_dir.resolve()
    logging.debug(f"Assemble directory: {assemble_dir}")
    assemble_dir.mkdir(parents=True, exist_ok=True)
    logging.debug(f"Ensuring assemble directory exists: {assemble_dir}")
    # Find the downloaded tar.gz
    tarballs = list(downloads_dir.glob("cpython*install_only_stripped*tar.gz"))
    if not tarballs:
        logging.error(f"No Python tarball found in {downloads_dir}")
        sys.exit(1)
    tarball = tarballs[0]
    if args.dry_run:
        logging.info(f"Dry run: Would extract {tarball} to {assemble_dir}")
        return
    shutil.unpack_archive(str(tarball), str(assemble_dir))
    logging.info(f"Extracted {tarball} to {assemble_dir}")


def run_pip_install(args):
    """Run pip install -r requirements.txt using the downloaded Python."""
    python_exe = args.python_executable or (args.assemble_dir / ("bin/python3" if os.name != "nt" else "python.exe"))
    requirements = args.requirements or "requirements.txt"
    cmd = [str(python_exe), "-m", "pip", "install", "-r", str(requirements)]
    if args.dry_run:
        logging.info(f"Dry run: Would run: {' '.join(cmd)}")
        return
    result = subprocess.run(cmd)
    if result.returncode != 0:
        logging.error(f"pip install failed with exit code {result.returncode}")
        sys.exit(result.returncode)


def run_npm_install(args):
    """Run npm install in the specified directory."""
    npm_exe = args.npm_executable or "npm"
    logging.debug(f"Using npm executable: {npm_exe}")
    cwd = args.directory or __here__
    logging.debug(f"Using working directory: {cwd}")
    cmd = f"{npm_exe} install --fetch-retries=5"
    logging.debug(f"Running command: {cmd} in {cwd}")
    if args.dry_run:
        logging.info(f"Dry run: Would run: {cmd} in {cwd}")
        return
    result = subprocess.run(cmd, cwd=str(cwd), shell=True)
    logging.debug(f"Command output: {result.stdout}")
    if result.returncode != 0:
        logging.error(f"npm install failed with exit code {result.returncode}")
        sys.exit(result.returncode)


def build_frontend(args):
    """Run npx webpack build."""
    npx_exe = args.npx_executable or "npx"
    logging.debug(f"Using npx executable: {npx_exe}")
    config = args.webpack_config or __here__ / "webpack.config.js"
    logging.debug(f"Using webpack config: {config}")
    cmd = f"{npx_exe} webpack --config {str(config)}"
    logging.debug(f"Running command: {cmd}")
    if args.dry_run:
        logging.info(f"Dry run: Would run: {cmd}")
        return
    result = subprocess.run(cmd, shell=True)
    logging.debug(f"Command output: {result.stdout}")
    if result.returncode != 0:
        logging.error(f"webpack build failed with exit code {result.returncode}")
        sys.exit(result.returncode)


def collectstatic(args):
    """Run manage.py collectstatic using the downloaded Python."""
    python_exe = args.python_executable or (args.assemble_dir / ("bin/python3" if os.name != "nt" else "python.exe"))
    manage_py = args.manage_py or __here__ / "manage.py"
    cmd = [str(python_exe), str(manage_py), "collectstatic", "--no-input"]
    if args.dry_run:
        logging.info(f"Dry run: Would run: {' '.join(cmd)}")
        return
    result = subprocess.run(cmd)
    if result.returncode != 0:
        logging.error(f"collectstatic failed with exit code {result.returncode}")
        sys.exit(result.returncode)


def stage_for_package(args):
    """Copy code/assets from repo root to assemble dir, excluding build artifacts and sensitive files. Optionally rename settings.py and urls.py."""
    src_root = args.src_root.resolve()
    dest_root = args.dest_root.resolve()
    exclude_dirs = {"dist", "build", ".venv", ".git", ".github", "__pycache__", "node_modules"}
    exclude_files = {"package-lock.json", ".gitignore"}
    exclude_patterns = ["*.log"]

    def should_exclude(path: pathlib.Path):
        # Exclude directories
        parts = set(path.parts)
        if parts & exclude_dirs:
            return True
        # Exclude files by name
        if path.name in exclude_files:
            return True
        # Exclude log files in log/
        if path.parent.name == "log" and path.suffix == ".log":
            return True
        # Exclude by pattern
        for pat in exclude_patterns:
            if path.match(pat):
                return True
        return False

    for item in src_root.iterdir():
        logging.debug(f"Considering copying {item}")
        if should_exclude(item):
            logging.info(f"Excluding {item}")
            continue
        dest = dest_root / item.name
        if args.dry_run:
            if item.is_dir():
                logging.info(f"Dry run: Would copy directory {item} to {dest}")
            elif item.is_file():
                logging.info(f"Dry run: Would copy file {item} to {dest}")
        else:
            if item.is_dir():
                logging.info(f"Copying directory {item} to {dest}")
                shutil.copytree(item, dest, dirs_exist_ok=True, ignore=shutil.ignore_patterns(*exclude_dirs, *exclude_files, *exclude_patterns))
            elif item.is_file():
                logging.info(f"Copying file {item} to {dest}")
                shutil.copy2(item, dest)

    # Optionally rename settings.py and urls.py
    if args.rename_settings:
        settings_file = dest_root / "delve" / "settings.py"
        urls_file = dest_root / "delve" / "urls.py"
        if args.dry_run:
            logging.info(f"Dry run: Would rename {settings_file} to {settings_file.parent / 'example-settings.py'}")
            logging.info(f"Dry run: Would rename {urls_file} to {urls_file.parent / 'example-urls.py'}")
        else:
            settings_file.rename(settings_file.parent / "example-settings.py")
            urls_file.rename(urls_file.parent / "example-urls.py")

def package(args):
    """Create a zip file containing everything needed to run an instance of delve."""
    plat, plat_str = get_platform()
    assemble_dir = args.assemble_dir.resolve()
    dist_dir = args.dist_dir.resolve()
    dist_dir.mkdir(parents=True, exist_ok=True)
    packaged_python = assemble_dir / "python"
    if plat == "windows":
        # Windows
        packaged_python = packaged_python / "python.exe"
    else:
        # Linux and MacOS
        packaged_python = packaged_python / "bin" / "python3"
    python_version = "unknown"
    if not args.dry_run:
        python_version = subprocess.check_output([str(packaged_python), "--version"]).decode().strip().split()[1]

    zip_name = args.output or dist_dir / f"DELVE_v{DELVE_VERSION}_cpython-{python_version}_{plat}.zip"
    exclude_patterns = ["node_modules", ".git", "*.log", "__pycache__", "build", "dist"]
    def exclude_func(dir, files):
        excluded = set()
        for pat in exclude_patterns:
            excluded.update({f for f in files if re.fullmatch(pat.replace("*", ".*"), f)})
        return excluded
    if args.dry_run:
        logging.info(f"Dry run: Would create zip {zip_name} from {assemble_dir}, excluding {exclude_patterns}")
        return
    shutil.make_archive(
        str(zip_name).replace('.zip',''),
        'zip',
        root_dir=assemble_dir,
        base_dir='.',
        logger=logging.getLogger(),
    )
    logging.info(f"Created package: {zip_name}")

    # Remove the python directory and create a second package without the interpreter
    python_dir = assemble_dir / "python"
    if python_dir.exists():
        if python_dir.is_dir():
            shutil.rmtree(python_dir)
        else:
            raise ValueError(f"Unexpected file type for python directory: {python_dir}")
        logging.info(f"Deleted python directory: {python_dir}")

    # Create second package filename (without python version)
    zip_name_no_python = args.output or (dist_dir / f"DELVE_v{DELVE_VERSION}_{plat}_update.zip")
    shutil.make_archive(
        str(zip_name_no_python).replace('.zip',''),
        'zip',
        root_dir=assemble_dir,
        base_dir='.',
        logger=logging.getLogger(),
    )
    logging.info(f"Created package without python: {zip_name_no_python}")


# --- Run All Steps ---
def run_all(args):
    """Run all steps in order: clean, download_python, extract_python, run_pip_install, run_npm_install, build_frontend, collectstatic, package."""
    logging.info("Starting clean step")
    clean_args = argparse.Namespace(
        all=args.clean_all,
        node=args.clean_node,
        python=args.clean_python,
        static=args.clean_static,
        extra=args.clean_extra,
        path=args.clean_path,
        dry_run=args.dry_run,
    )
    clean(clean_args)

    logging.info("Starting download step")
    download_args = argparse.Namespace(
        target_dir=args.download_target_dir,
        dry_run=args.dry_run,
    )
    download_python(download_args)

    logging.info("Starting extract step")
    extract_args = argparse.Namespace(
        downloads_dir=args.extract_downloads_dir,
        assemble_dir=args.extract_assemble_dir,
        dry_run=args.dry_run,
    )
    extract_python(extract_args)

    logging.info("Starting pip install step")
    pip_args = argparse.Namespace(
        python_executable=args.pip_python_executable,
        requirements=args.pip_requirements,
        assemble_dir=args.pip_assemble_dir,
        dry_run=args.dry_run,
    )
    run_pip_install(pip_args)

    logging.info("Starting npm install step")
    npm_args = argparse.Namespace(
        npm_executable=args.npm_npm_executable,
        directory=args.npm_directory,
        dry_run=args.dry_run,
    )
    run_npm_install(npm_args)

    logging.info("Starting frontend build step")
    frontend_args = argparse.Namespace(
        npx_executable=args.frontend_npx_executable,
        webpack_config=args.frontend_webpack_config,
        dry_run=args.dry_run,
    )
    build_frontend(frontend_args)

    logging.info("Starting collectstatic step")
    static_args = argparse.Namespace(
        python_executable=args.static_python_executable,
        manage_py=args.static_manage_py,
        assemble_dir=args.static_assemble_dir,
        dry_run=args.dry_run,
    )
    collectstatic(static_args)

    logging.info("Starting stage for package step")
    stage_args = argparse.Namespace(
        src_root=args.stage_src_root,
        dest_root=args.stage_dest_root,
        rename_settings=args.stage_rename_settings,
        dry_run=args.dry_run,
    )
    stage_for_package(stage_args)

    logging.info("Starting package step")
    package_args = argparse.Namespace(
        assemble_dir=args.package_assemble_dir,
        dist_dir=args.package_dist_dir,
        output=args.package_output,
        dry_run=args.dry_run,
    )
    package(package_args)

# --- Argument Parsing ---
def main():
    parser = argparse.ArgumentParser(description="Delve Bootstrap Script")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="Set the logging level")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done, but don't make changes")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # clean
    clean_parser = subparsers.add_parser("clean", help="Clean up build artifacts and other files")
    clean_parser.add_argument("--all", action="store_true", help="Clean all typical build artifacts")
    clean_parser.add_argument("--node", action="store_true", help="Clean node-related files")
    clean_parser.add_argument("--python", action="store_true", help="Clean python-related files")
    clean_parser.add_argument("--static", action="store_true", help="Clean staticfiles")
    clean_parser.add_argument("--extra", nargs="*", help="Extra patterns to clean")
    clean_parser.add_argument("--path", type=pathlib.Path, default=__here__, help="Base path to clean from")
    clean_parser.set_defaults(func=clean)

    # download_python
    dl_parser = subparsers.add_parser("download_python", help="Download Python standalone for this platform")
    dl_parser.add_argument("--target-dir", type=pathlib.Path, default=__here__/"build"/"downloads", help="Where to download Python")
    dl_parser.set_defaults(func=download_python)

    # extract_python
    extract_parser = subparsers.add_parser("extract_python", help="Extract downloaded Python to assemble dir")
    extract_parser.add_argument("--downloads-dir", type=pathlib.Path, default=__here__/"build"/"downloads", help="Where Python tarball is")
    extract_parser.add_argument("--assemble-dir", type=pathlib.Path, default=__here__/"build"/"assemble", help="Where to extract Python")
    extract_parser.set_defaults(func=extract_python)

    # run_pip_install
    pip_parser = subparsers.add_parser("run_pip_install", help="Run pip install -r requirements.txt using downloaded Python")
    pip_parser.add_argument("--python-executable", type=pathlib.Path, help="Python executable to use")
    pip_parser.add_argument("--requirements", type=pathlib.Path, help="Requirements file to use")
    pip_parser.add_argument("--assemble-dir", type=pathlib.Path, default=__here__/"build"/"assemble"/"python", help="Where Python is extracted")
    pip_parser.set_defaults(func=run_pip_install)

    # run_npm_install
    npm_parser = subparsers.add_parser("run_npm_install", help="Run npm install in the specified directory")
    npm_parser.add_argument("--npm-executable", default="npm", help="npm executable to use")
    npm_parser.add_argument("--directory", type=pathlib.Path, default=__here__, help="Directory to run npm install in")
    npm_parser.set_defaults(func=run_npm_install)

    # build_frontend
    frontend_parser = subparsers.add_parser("build_frontend", help="Run npx webpack build")
    frontend_parser.add_argument("--npx-executable", default="npx", help="npx executable to use")
    frontend_parser.add_argument("--webpack-config", type=pathlib.Path, default=__here__/"webpack.config.js", help="Webpack config file")
    frontend_parser.set_defaults(func=build_frontend)

    # collectstatic
    static_parser = subparsers.add_parser("collectstatic", help="Run manage.py collectstatic using downloaded Python")
    static_parser.add_argument("--python-executable", type=pathlib.Path, help="Python executable to use")
    static_parser.add_argument("--manage-py", type=pathlib.Path, default=__here__/"manage.py", help="manage.py location")
    static_parser.add_argument("--assemble-dir", type=pathlib.Path, default=__here__/"build"/"assemble"/"python", help="Where Python is extracted")
    static_parser.set_defaults(func=collectstatic)

    # Stage
    stage_parser = subparsers.add_parser("stage_for_package", help="Copy code/assets to assemble dir for packaging, excluding build artifacts and sensitive files.")
    stage_parser.add_argument("--src-root", type=pathlib.Path, default=__here__, help="Repo root to copy from")
    stage_parser.add_argument("--dest-root", type=pathlib.Path, default=__here__/"build"/"assemble", help="Destination assemble dir")
    stage_parser.add_argument("--rename-settings", action="store_true", default=True, help="Rename settings.py and urls.py to example-*.py (default: True)")
    stage_parser.add_argument("--no-rename-settings", dest="rename_settings", action="store_false", help="Do not rename settings.py and urls.py")
    stage_parser.set_defaults(func=stage_for_package)

    # package
    package_parser = subparsers.add_parser("package", help="Create a zip file for deployment")
    package_parser.add_argument("--assemble-dir", type=pathlib.Path, default=__here__/"build"/"assemble", help="Directory to package")
    package_parser.add_argument("--dist-dir", type=pathlib.Path, default=__here__/"dist", help="Where to put the zip")
    package_parser.add_argument("--output", type=pathlib.Path, help="Output zip file name")
    package_parser.set_defaults(func=package)

    # all
    all_parser = subparsers.add_parser("all", help="Run all steps in order")
    # Clean args
    all_parser.add_argument("--clean-all", action="store_true", help="Clean all typical build artifacts")
    all_parser.add_argument("--clean-node", action="store_true", help="Clean node-related files")
    all_parser.add_argument("--clean-python", action="store_true", help="Clean python-related files")
    all_parser.add_argument("--clean-static", action="store_true", help="Clean staticfiles")
    all_parser.add_argument("--clean-extra", nargs="*", help="Extra patterns to clean")
    all_parser.add_argument("--clean-path", type=pathlib.Path, default=__here__, help="Base path to clean from")
    # Download Python args
    all_parser.add_argument("--download-target-dir", type=pathlib.Path, default=__here__/"build"/"downloads", help="Where to download Python")
    # Extract Python args
    all_parser.add_argument("--extract-downloads-dir", type=pathlib.Path, default=__here__/"build"/"downloads", help="Where Python tarball is")
    all_parser.add_argument("--extract-assemble-dir", type=pathlib.Path, default=__here__/"build"/"assemble", help="Where to extract Python")
    # pip install args
    all_parser.add_argument("--pip-python-executable", type=pathlib.Path, help="Python executable to use for pip install")
    all_parser.add_argument("--pip-requirements", type=pathlib.Path, help="Requirements file to use for pip install")
    all_parser.add_argument("--pip-assemble-dir", type=pathlib.Path, default=__here__/"build"/"assemble"/"python", help="Where Python is extracted for pip install")
    # npm install args
    all_parser.add_argument("--npm-npm-executable", default="npm", help="npm executable to use for npm install")
    all_parser.add_argument("--npm-directory", type=pathlib.Path, default=__here__, help="Directory to run npm install in")
    # build_frontend args
    all_parser.add_argument("--frontend-npx-executable", default="npx", help="npx executable to use for webpack build")
    all_parser.add_argument("--frontend-webpack-config", type=pathlib.Path, default=__here__/"webpack.config.js", help="Webpack config file for frontend build")
    # collectstatic args
    all_parser.add_argument("--static-python-executable", type=pathlib.Path, help="Python executable to use for collectstatic")
    all_parser.add_argument("--static-manage-py", type=pathlib.Path, default=__here__/"manage.py", help="manage.py location for collectstatic")
    all_parser.add_argument("--static-assemble-dir", type=pathlib.Path, default=__here__/"build"/"assemble"/"python", help="Where Python is extracted for collectstatic")
    # stage_for_package args
    all_parser.add_argument("--stage-src-root", type=pathlib.Path, default=__here__, help="Source root for staging")
    all_parser.add_argument("--stage-dest-root", type=pathlib.Path, default=__here__/"build"/"assemble", help="Destination root for staging")
    all_parser.add_argument("--stage-rename-settings", action="store_true", default=True, help="Rename settings.py and urls.py to example-*.py (default: True)")
    all_parser.add_argument("--stage-no-rename-settings", dest="stage_rename_settings", action="store_false", help="Do not rename settings.py and urls.py")
    # package args
    all_parser.add_argument("--package-assemble-dir", type=pathlib.Path, default=__here__/"build"/"assemble", help="Directory to package")
    all_parser.add_argument("--package-dist-dir", type=pathlib.Path, default=__here__/"dist", help="Where to put the zip")
    all_parser.add_argument("--package-output", type=pathlib.Path, help="Output zip file name")
    all_parser.set_defaults(func=run_all)

    args = parser.parse_args()
    setup_logging(args.log_level)
    args.func(args)

if __name__ == "__main__":
    main()
