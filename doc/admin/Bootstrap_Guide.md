# Bootstrap Guide

The `bootstrap.py` script automates building and packaging Delve. Each step is a standalone subcommand so you can run parts individually or compose your own pipeline. A `--dry-run` flag is available on every command to show actions without making changes.

## Subcommands

### `clean`
Remove build artefacts such as `build/`, `dist/`, `staticfiles/` and more.

```bash
python bootstrap.py clean --all
python bootstrap.py clean --node --python --path /tmp/workdir
```

### `download_python`
Download the latest prebuilt CPython archive for the current platform.

```bash
python bootstrap.py download_python --target-dir build/downloads
```

### `extract_python`
Extract a previously downloaded archive into an assemble directory.

```bash
python bootstrap.py extract_python \
    --downloads-dir build/downloads \
    --assemble-dir build/assemble
```

### `run_pip_install`
Install Python requirements into the assembled Python environment.

```bash
python bootstrap.py run_pip_install \
    --python-executable build/assemble/python/python3 \
    --requirements requirements.txt
```

### `run_npm_install`
Install JavaScript dependencies for the frontend.

```bash
python bootstrap.py run_npm_install --directory .
```

### `build_frontend`
Use Webpack to build the browser assets.

```bash
python bootstrap.py build_frontend --webpack-config webpack.config.js
```

### `collectstatic`
Run Django's `collectstatic` using the assembled Python.

```bash
python bootstrap.py collectstatic \
    --python-executable build/assemble/python/python3 \
    --manage-py manage.py
```

### `stage_for_package`
Copy source code and assets into a staging directory, optionally renaming `settings.py` and `urls.py`.

```bash
python bootstrap.py stage_for_package \
    --src-root . \
    --dest-root build/assemble
```

### `package`
Create a distributable zip from the staged directory.

```bash
python bootstrap.py package \
    --assemble-dir build/assemble \
    --dist-dir dist \
    --output delve.zip
```

### `all`
Run all of the above steps in sequence. Each nested step respects the global options.

```bash
python bootstrap.py all --clean-all --download-target-dir build/downloads
```

## Extending with modular hooks

Because every subcommand is a normal Python function, you can override or extend behaviour by importing `bootstrap` and replacing functions before calling `main()`. This makes it easy to add pre‑ or post‑steps without modifying the original script.

```python
# custom_bootstrap.py
import bootstrap

def custom_package(args):
    print("Signing package")
    bootstrap.package(args)
    subprocess.run(["gpg", "--sign", str(args.output)])

bootstrap.package = custom_package

if __name__ == "__main__":
    bootstrap.main()
```

Running `python custom_bootstrap.py package --assemble-dir build/assemble` executes the standard packaging step and then signs the resulting archive. Similar wrappers can intercept any other subcommand or compose entirely new workflows.
