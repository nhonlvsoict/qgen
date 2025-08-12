from typer.testing import CliRunner
from qsg import cli


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
