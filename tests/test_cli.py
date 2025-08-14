from typer.testing import CliRunner
from qsg import cli
import sys
from types import SimpleNamespace


class DummyAdapter:
    name = 'dummy'

    def required_ir(self):
        return 'ir'

    def prepare_payload(self, ir_artifact):
        assert ir_artifact == 'ir_artifact'
        return {'file.txt': 'content'}

    def runtime_packages(self):
        return []

    def entrypoint(self):
        return 'print(42)'


def test_build_with_config(monkeypatch, tmp_path):
    src = tmp_path / 'src.py'
    src.write_text('print(42)')
    cfg = tmp_path / 'cfg.yaml'
    cfg.write_text('target: ibm\n')

    monkeypatch.setattr(cli.adapters_base, 'load_adapter', lambda *a, **k: DummyAdapter())
    monkeypatch.setattr(cli, 'lower_to_ir', lambda *a, **k: 'ir_artifact')
    monkeypatch.setattr(cli, 'build_image', lambda *a, **k: 'tag')

    runner = CliRunner()
    result = runner.invoke(cli.app, ['build', str(src), '--config', str(cfg)])
    assert result.exit_code == 0
    assert 'Built tag' in result.stdout


def test_build_with_detection(monkeypatch, tmp_path):
    src = tmp_path / 'src.py'
    src.write_text('print(42)')

    monkeypatch.setattr('qsg.detect.detect_language_and_provider', lambda path: ('python', 'ibm'))
    monkeypatch.setattr(cli.adapters_base, 'load_adapter', lambda *a, **k: DummyAdapter())
    monkeypatch.setattr(cli, 'lower_to_ir', lambda *a, **k: 'ir_artifact')
    monkeypatch.setattr(cli, 'build_image', lambda *a, **k: 'tag')

    runner = CliRunner()
    result = runner.invoke(cli.app, ['build', str(src)])
    assert result.exit_code == 0
    assert 'Built tag' in result.stdout


def test_build_requires_target(monkeypatch, tmp_path):
    src = tmp_path / 'src.py'
    src.write_text('print(42)')
    monkeypatch.setattr('qsg.detect.detect_language_and_provider', lambda path: (None, None))

    runner = CliRunner()
    result = runner.invoke(cli.app, ['build', str(src)])
    assert result.exit_code != 0


def test_run_local_with_env(monkeypatch):
    captured = {}

    def dummy_run(image, detach=False, remove=True, environment=None):
        captured['env'] = environment
        return b''

    dummy_client = SimpleNamespace(containers=SimpleNamespace(run=dummy_run))
    fake_docker = SimpleNamespace(from_env=lambda: dummy_client)
    monkeypatch.setitem(sys.modules, 'docker', fake_docker)

    runner = CliRunner()
    result = runner.invoke(
        cli.app,
        ['run-local', 'img', '-e', 'IBM_TOKEN=foo', '-e', 'X=Y'],
    )
    assert result.exit_code == 0
    assert captured['env'] == {'IBM_TOKEN': 'foo', 'X': 'Y'}
