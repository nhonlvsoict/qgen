import json
from qsg.config import BuildConfig

def test_buildconfig_from_yaml(tmp_path):
    cfg_file = tmp_path / 'config.yaml'
    cfg_file.write_text('target: ibm\nprofile: base\nimage: test:latest\nworkdir: build\nexecution_mode: session\n')
    cfg = BuildConfig.from_file(cfg_file)
    assert cfg.target == 'ibm'
    assert cfg.profile == 'base'
    assert cfg.image == 'test:latest'
    assert cfg.workdir == 'build'
    assert cfg.execution_mode == 'session'

def test_buildconfig_from_json(tmp_path):
    cfg_file = tmp_path / 'config.json'
    cfg_file.write_text(json.dumps({'target': 'ibm', 'profile': 'base'}))
    cfg = BuildConfig.from_file(cfg_file)
    assert cfg.target == 'ibm'
    assert cfg.profile == 'base'
