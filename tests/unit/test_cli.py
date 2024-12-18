import pytest
from typer.testing import CliRunner
from seqerakit.cli import app
import tempfile
import os

runner = CliRunner()


@pytest.mark.xfail(reason="Not implemented")
def test_cli_version():
    """Test the version output"""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "seqerakit" in result.stdout


def test_cli_help():
    """Test the help output"""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Process YAML configuration files to manage Seqera Platform resources." in result.stdout


def test_cli_info():
    """Test the info command"""
    result = runner.invoke(app, ["--info"])
    assert result.exit_code == 0


def test_cli_no_yaml():
    """Test error when no YAML is provided"""
    result = runner.invoke(app)
    assert result.exit_code == 1
    # FIXME assert "No YAML" in result.stdout


def test_cli_invalid_yaml():
    """Test error with invalid YAML file"""
    with tempfile.NamedTemporaryFile(suffix=".yml") as tmp:
        tmp.write(b"invalid: - yaml: content")
        tmp.flush()
        result = runner.invoke(app, [tmp.name, "--dryrun"])
        assert result.exit_code == 1


def test_cli_dryrun():
    """Test dryrun mode with valid YAML"""
    yaml_content = """
launch:
  - name: 'test-pipeline'
    workspace: 'test/workspace'
    compute-env: 'test-env'
    pipeline: 'https://github.com/test/pipeline'
"""
    with tempfile.NamedTemporaryFile(suffix=".yml", mode="w") as tmp:
        tmp.write(yaml_content)
        tmp.flush()
        result = runner.invoke(app, [tmp.name, "--dryrun"])
        assert result.exit_code == 0


def test_cli_targets():
    """Test targeting specific resources"""
    yaml_content = """
pipelines:
  - name: 'test-pipeline'
    url: 'https://github.com/test/pipeline'
    workspace: 'test/workspace'
launch:
  - name: 'test-launch'
    workspace: 'test/workspace'
    pipeline: 'https://github.com/test/pipeline'
"""
    with tempfile.NamedTemporaryFile(suffix=".yml", mode="w") as tmp:
        tmp.write(yaml_content)
        tmp.flush()
        result = runner.invoke(app, [tmp.name, "--targets", "pipelines", "--dryrun"])
        assert result.exit_code == 0


def test_cli_json_output():
    """Test JSON output format"""
    yaml_content = """
launch:
  - name: 'test-pipeline'
    workspace: 'seqeralabs/scidev-testing'
    compute-env: 'seqera_aws_london_fusion_nvme'
    pipeline: 'https://github.com/test/pipeline'
"""
    with tempfile.NamedTemporaryFile(suffix=".yml", mode="w") as tmp:
        tmp.write(yaml_content)
        tmp.flush()
        result = runner.invoke(app, [tmp.name, "--json", "--dryrun"])
        assert result.exit_code == 0


def test_cli_log_level():
    """Test different log levels"""
    yaml_content = """
launch:
  - name: 'test-pipeline'
    workspace: 'seqeralabs/scidev-testing'
    compute-env: 'seqera_aws_london_fusion_nvme'
    pipeline: 'https://github.com/test/pipeline'
"""
    with tempfile.NamedTemporaryFile(suffix=".yml", mode="w") as tmp:
        tmp.write(yaml_content)
        tmp.flush()
        result = runner.invoke(app, [tmp.name, "--log-level", "DEBUG", "--dryrun"])
        assert result.exit_code == 0


def test_cli_delete():
    """Test delete mode"""
    yaml_content = """
pipelines:
  - name: 'test-pipeline'
    url: 'https://github.com/test/pipeline'
    workspace: 'seqeralabs/scidev-testing'
"""
    with tempfile.NamedTemporaryFile(suffix=".yml", mode="w") as tmp:
        tmp.write(yaml_content)
        tmp.flush()
        result = runner.invoke(app, [tmp.name, "--delete", "--dryrun"])
        assert result.exit_code == 0


def test_cli_additional_args():
    """Test passing additional CLI arguments"""
    yaml_content = """
launch:
  - name: 'test-pipeline'
    workspace: 'test/workspace'
    compute-env: 'test-env'
    pipeline: 'https://github.com/test/pipeline'
"""
    with tempfile.NamedTemporaryFile(suffix=".yml", mode="w") as tmp:
        tmp.write(yaml_content)
        tmp.flush()
        result = runner.invoke(app, [tmp.name, "--cli", "--insecure", "--dryrun"])
        assert result.exit_code == 0
