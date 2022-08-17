import os
from datetime import datetime
from importlib import import_module


class Config:
    """A parser for config file."""
    @staticmethod
    def from_str_to_class(name, package, cls_name):
        """Convert name to class.

        This function converts the name of class in config
        to a Class. The function gets the 'cls_name' attribute
        from the 'mod' object of the imported module with
        absolute path 'package.name'.

        Args:
            name (str): The name of the module in which the class
                is located.
            package (str): The name of the package relative to
                which the module is imported.
            cls_name (str): The name of the class.

        Returns:
            (package.name.cls_name): The class with name cls_name.

        Examples:
        >>> Config.from_str_to_class(
                name='RSIStrategy',
                package='Strategy',
                cls_name='RSIStrategy'
            )
        <class 'Strategy.RSIStrategy.RSIStrategy'>
        """
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
        """Convert name to Futu attribute.

        Args:
            name (str): The name of Futu attribute.

        Returns:
            (futu.futu_attr.sub_attr): The Futu attribute with name
                'name'.

        Examples:
        >>> Config.from_str_to_futu_attr('TrdMarket.HK')
        HK
        >>> Config.from_str_to_futu_attr('SecurityFirm.FUTUSECURITIES')
        FUTUSECURITIES
        """
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
        """Parse the config file with path cfg_pth.

        This function parses the config file with a cfg dict
        and converts the names to Class and Futu attributes.

        Args:
            cfg_pth (str): The path of the config file, can be
                absolute or relative.

        Returns:
            cfg_dict (dict[dict]): A dict of config with keys
                'account', 'historical_quote_dates', 'indicators',
                'stocks_of_interest', 'strategy'. The 'account'
                contains Futu attributes, and the name of 'strategy'
                is now converted to class.
        """
        if not isinstance(cfg_pth, str):
            raise TypeError(f'Only str type is supported for cfg_pth, '
                            f'but got {type(cfg_pth)}')

        if not os.path.exists(cfg_pth):
            raise OSError(
                'The config file path {cfg_pth} does not exist.'.format(
                    cfg_pth=cfg_pth))

        cfg_pth = os.path.splitext(cfg_pth)[0]
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
