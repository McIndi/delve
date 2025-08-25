
"""
Sanity checks for delve-reorg/bootstrap.py subcommands using unittest.
"""
import subprocess
import unittest
import tempfile
import pathlib
import sys

BOOTSTRAP = pathlib.Path(__file__).parent / "bootstrap.py"
PYTHON = pathlib.Path(sys.executable)

def run_bootstrap(args, cwd=None, env=None):
    cmd = [str(PYTHON), str(BOOTSTRAP)] + args
    result = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)
    return result


class TestBootstrap(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.tmp_path = pathlib.Path(self.tmpdir.name)
        # Create default structure
        (self.tmp_path / "build" / "downloads").mkdir(parents=True)
        (self.tmp_path / "build" / "assemble").mkdir(parents=True)
        (self.tmp_path / "build" / "assemble" / "python").mkdir(parents=True)
        (self.tmp_path / "dist").mkdir(parents=True)
        (self.tmp_path / "__pycache__").mkdir(parents=True)
        (self.tmp_path / "test.log").write_text("log")
        (self.tmp_path / "webpack.config.js").write_text("")
        (self.tmp_path / "manage.py").write_text("")
        (self.tmp_path / "requirements.txt").write_text("")

    def tearDown(self):
        self.tmpdir.cleanup()


    def test_clean_dry_run(self):
        result = run_bootstrap([
            "--dry-run", "clean", "--all", "--path", str(self.tmp_path)
        ])
        self.assertEqual(result.returncode, 0)
        self.assertTrue("Would remove" in result.stdout or result.stderr)


    def test_download_python_dry_run(self):
        downloads_dir = self.tmp_path / "build" / "downloads"
        result = run_bootstrap([
            "--dry-run", "download_python", "--target-dir", str(downloads_dir)
        ])
        self.assertEqual(result.returncode, 0)
        self.assertTrue("Would download" in result.stdout or result.stderr)


    def test_extract_python_dry_run(self):
        downloads_dir = self.tmp_path / "build" / "downloads"
        assemble_dir = self.tmp_path / "build" / "assemble"
        # Always create a fake tarball so extract_python finds it, even in dry run
        tarball = downloads_dir / "cpython-test-install_only_stripped.tar.gz"
        tarball.write_text("")
        result = run_bootstrap([
            "--dry-run", "extract_python",
            "--downloads-dir", str(downloads_dir),
            "--assemble-dir", str(assemble_dir),
        ])
        self.assertEqual(result.returncode, 0)
        self.assertTrue("Would extract" in result.stdout or result.stderr)


    def test_run_pip_install_dry_run(self):
        assemble_python_dir = self.tmp_path / "build" / "assemble" / "python"
        fake_python = assemble_python_dir / "python3"
        fake_python.write_text("")
        fake_python.chmod(0o755)
        reqs = self.tmp_path / "requirements.txt"
        result = run_bootstrap([
            "--dry-run", "run_pip_install",
            "--python-executable", str(fake_python),
            "--requirements", str(reqs),
            "--assemble-dir", str(assemble_python_dir)
        ])
        self.assertEqual(result.returncode, 0)
        self.assertTrue("Would run" in result.stdout or result.stderr)


    def test_run_npm_install_dry_run(self):
        result = run_bootstrap([
            "--dry-run", "run_npm_install",
            "--directory", str(self.tmp_path)
        ])
        self.assertEqual(result.returncode, 0)
        self.assertTrue("Would run" in result.stdout or result.stderr)


    def test_build_frontend_dry_run(self):
        config = self.tmp_path / "webpack.config.js"
        result = run_bootstrap([
            "--dry-run", "build_frontend",
            "--webpack-config", str(config)
        ])
        self.assertEqual(result.returncode, 0)
        self.assertTrue("Would run" in result.stdout or result.stderr)


    def test_collectstatic_dry_run(self):
        assemble_python_dir = self.tmp_path / "build" / "assemble" / "python"
        fake_python = assemble_python_dir / "python3"
        fake_python.write_text("")
        fake_python.chmod(0o755)
        fake_manage = self.tmp_path / "manage.py"
        result = run_bootstrap([
            "--dry-run", "collectstatic",
            "--python-executable", str(fake_python),
            "--manage-py", str(fake_manage),
            "--assemble-dir", str(assemble_python_dir)
        ])
        self.assertEqual(result.returncode, 0)
        self.assertTrue("Would run" in result.stdout or result.stderr)


    def test_stage_for_package_dry_run(self):
        src = self.tmp_path
        dest = self.tmp_path / "build" / "assemble"
        result = run_bootstrap([
            "--dry-run", "stage_for_package",
            "--src-root", str(src),
            "--dest-root", str(dest)
        ])
        self.assertEqual(result.returncode, 0)
        # Should not error


    def test_package_dry_run(self):
        assemble = self.tmp_path / "build" / "assemble"
        dist = self.tmp_path / "dist"
        (assemble / "foo.txt").write_text("")
        result = run_bootstrap([
            "--dry-run", "package",
            "--assemble-dir", str(assemble),
            "--dist-dir", str(dist),
            "--output", str(dist / "out.zip")
        ])
        self.assertEqual(result.returncode, 0)
        self.assertTrue("Would create zip" in result.stdout or result.stderr)


    def test_all_dry_run(self):
        # This will run all steps in dry-run mode, using the correct structure
        downloads_dir = self.tmp_path / "build" / "downloads"
        downloads_dir.mkdir(parents=True, exist_ok=True)
        tarball = downloads_dir / "cpython-test-install_only_stripped.tar.gz"
        tarball.write_text("")
        tmp = self.tmp_path
        result = run_bootstrap([
            "--dry-run", "all",
            "--clean-path", str(tmp),
            "--download-target-dir", str(tmp / "build" / "downloads"),
            "--extract-downloads-dir", str(tmp / "build" / "downloads"),
            "--extract-assemble-dir", str(tmp / "build" / "assemble"),
            "--pip-assemble-dir", str(tmp / "build" / "assemble" / "python"),
            "--npm-directory", str(tmp),
            "--frontend-webpack-config", str(tmp / "webpack.config.js"),
            "--static-assemble-dir", str(tmp / "build" / "assemble" / "python"),
            "--stage-src-root", str(tmp),
            "--stage-dest-root", str(tmp / "build" / "assemble"),
            "--package-assemble-dir", str(tmp / "build" / "assemble"),
            "--package-dist-dir", str(tmp / "dist"),
        ])
        self.assertEqual(result.returncode, 0)
        self.assertTrue("Dry run" in result.stdout or result.stderr)

if __name__ == "__main__":
    unittest.main()
