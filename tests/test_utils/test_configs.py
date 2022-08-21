import pytest

from utils.config import Config


@pytest.mark.parametrize('cfg_file', ['demo/configs/futubot_config_demo.py'])
def test_parse_config(cfg_file):
    with pytest.raises(TypeError):
        Config.parse_config(123456)
    
    with pytest.raises(OSError):
        Config.parse_config('demo/config.py')
    
    cfg_dict = Config.parse_config(cfg_pth=cfg_file)

    assert cfg_dict['account']['filter_trdmarket'] == 'HK'
    assert cfg_dict['account']['security_firm'] == 'FUTUSECURITIES'
    assert isinstance(cfg_dict['strategy']['name'], type)
