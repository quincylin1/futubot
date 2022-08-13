import os.path as osp
from datetime import datetime
from importlib import import_module


class Config:
    @staticmethod
    def from_str_to_class(name, package, cls_name):

        if not isinstance(name, str):
            raise TypeError(f'Only str type is supported for name, '
                            f'but got {type(name)}')
        if not isinstance(package, str):
            raise TypeError(f'Only str type is supported for package, '
                            f'but got {type(package)}')
        if not isinstance(cls_name, str):
            raise TypeError(f'Only str type is supported for cls_name, '
                            f'but got {type(cls_name)}')

        name = '.' + name
        mod = import_module(name, package)
        return getattr(mod, cls_name)

    @staticmethod
    def from_str_to_futu_attr(name):

        if not isinstance(name, str):
            raise TypeError(f'Only str type is supported for name, '
                            f'but got {type(name)}')

        mod = import_module('futu')
        attributes = name.split('.')
        futu_attr_str = attributes[0]
        sub_attr_str = attributes[1]

        futu_attr = getattr(mod, futu_attr_str)
        sub_attr = getattr(futu_attr, sub_attr_str)

        return sub_attr

    @staticmethod
    def parse_config(cfg_pth):

        if not isinstance(cfg_pth, str):
            raise TypeError(f'Only str type is supported for cfg_pth, '
                            f'but got {type(cfg_pth)}')

        cfg_pth = osp.splitext(cfg_pth)[0]
        cfg_pth = cfg_pth.replace('/', '.')
        mod = import_module(cfg_pth)

        for name, value in mod.__dict__.items():
            if not name.startswith('__'):
                cfg_dict = value

        cfg_dict['account']['filter_trdmarket'] = Config.from_str_to_futu_attr(
            cfg_dict['account']['filter_trdmarket'])
        cfg_dict['account']['security_firm'] = Config.from_str_to_futu_attr(
            cfg_dict['account']['security_firm'])

        if cfg_dict['historical_quote_dates']['end_date'] is None:
            cfg_dict['historical_quote_dates']['end_date'] = datetime.today(
            ).strftime('%Y-%m-%d %H:%M:%S')

        cfg_dict['strategy']['name'] = Config.from_str_to_class(
            name=cfg_dict['strategy']['name'],
            package='Strategy',
            cls_name=cfg_dict['strategy']['name'])

        return cfg_dict
