from src import hint_cli, hint_deploy


def test_production_uses_real_adr():
    cfg = hint_deploy.HintConfig("config", "production")
    assert cfg.hint_adr_url == "https://adr.unaids.org/"


def test_real_adr_optional():
    cfg = hint_deploy.HintConfig("config")
    assert cfg.hint_adr_url is None


def test_production_and_staging_use_real_email_configuration():
    cfg = hint_deploy.HintConfig("config", "production")
    assert cfg.hint_email_mode == "real"
    cfg = hint_deploy.HintConfig("config", "staging")
    assert cfg.hint_email_mode == "real"


def test_base_uses_fake_email_configuration():
    cfg = hint_deploy.HintConfig("config")
    assert cfg.hint_email_mode == "disk"


def test_proxy_url_drops_port_appropriately():
    assert hint_deploy.proxy_url("example.com", 443) == \
        "https://example.com"
    assert hint_deploy.proxy_url("example.com", 1443) == \
        "https://example.com:1443"


def test_load_and_reload_config():
    path = "config"
    config = "production"
    cfg = hint_deploy.HintConfig(path, config)
    cfg.hint_tag = "develop"
    hint_cli.save_config(path, config, cfg)

    hint_cli.read_config(path)

    config_name, config_value = hint_cli.load_config(path, None)
    assert config_value.hint_tag == "master"
    assert config_name == "production"
    hint_cli.remove_config(path)
