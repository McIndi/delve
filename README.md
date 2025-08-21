# Delve

Delve is a powerful, extensible platform for ingesting, transforming, and searching structured, unstructured, and semi-structured data. It is designed for easy local development, robust production deployments, and seamless integration with modern tools and containerization workflows.

## Features
- Ingest data from diverse sources (REST API, file tail, syslog, scheduled queries)
- Transform and normalize data with custom pipelines
- Perform powerful search and filtering with a pipeline syntax
- Create interactive dashboards and visualizations
- Set up alerts and notifications
- Extend functionality with custom apps and commands

## Project Structure
- `manage.py` at the repository root for standard Django management
- Core apps (e.g., `events`, `users`) and configuration in top-level folders
- `requirements.txt` and `pyproject.toml` for Python dependencies
- `bootstrap.py` for automated build, packaging, and asset management
- `frontend/` for JavaScript and SCSS assets
- `doc/` for user and admin documentation

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/notesofcliff/delve
cd delve
```

### 2. Create and activate a virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate  # On Windows
source .venv/bin/activate  # On Linux/macOS
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
# or, for editable/dev install:
pip install -e .
```

### 4. Run database migrations
```bash
python manage.py migrate
```

### 5. Install frontend dependencies and build assets
```bash
npm install
npx webpack --config webpack.config.js
```

### 6. Collect static files
```bash
python manage.py collectstatic --no-input
```


### 7. Create a superuser
```bash
python manage.py createsuperuser
```

### 8. Start the development server
```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000/ in your browser to access the web UI.

## Advanced: Automated Build & Packaging For Air-Gapped Systems

### Automated Build & Packaging for Air-Gapped Systems

You can use `bootstrap.py` to automate building, packaging, and asset management for deployment to air-gapped systems. While containerization is also supported, this utility enables deployment to air-gapped environments without requiring dependencies on the target system.

After running the following commands, you will have a zip file under `./dist/` containing everything needed to deploy Delve to an air-gapped system, including source code, Python interpreter, frontend and backend dependencies, and more:

- Clean build artefacts:
  ```bash
  python bootstrap.py clean --all
  ```
- Download and extract Python:
  ```bash
  python bootstrap.py download_python
  python bootstrap.py extract_python
  ```
- Install Python dependencies:
  ```bash
  python bootstrap.py run_pip_install
  ```
- Install frontend dependencies and build assets:
  ```bash
  python bootstrap.py run_npm_install
  python bootstrap.py build_frontend
  ```
- Collect static files:
  ```bash
  python bootstrap.py collectstatic
  ```
- Package everything:
  ```bash
  python bootstrap.py package
  ```

Or run all steps in sequence:
```bash
python bootstrap.py all
```

See `doc/admin/Bootstrap_Guide.md` for full details and extensibility options.

## Documentation
- **User Guide:** `doc/user/Getting_Started.md`
- **Admin Guide:** `doc/admin/Installation_and_Setup.md`, `doc/admin/Bootstrap_Guide.md`
- **API Reference:** Browse the REST API via the web UI after starting the server

## Key Concepts
- **Events:** The core data unit, with indexed and extracted fields
- **Queries:** Pipeline-based data retrieval and transformation
- **Ingestion:** Multiple methods, including REST, file tail, and syslog
- **Field Extraction:** Index-time and search-time extraction
- **Custom Apps:** Extend Delve with new commands, dashboards, and APIs
- **Alerts:** Search-based and processor-based alerting

## Contributing
Contributions are welcome! Please see the documentation and open an issue or pull request.

## License
Delve is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0). See `doc/LICENSES.txt` for details.
