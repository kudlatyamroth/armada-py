import os
import json


class Config(object):
    config_paths = []

    @staticmethod
    def get(file_name, default=None):
        config = {}
        file_list = Config._get_path(file_name)
        if not file_list:
            if not default:
                return config
            return default
        config = {}
        for file in file_list:
            config = Config._merge_config(config, Config._load(file))
        return config

    @staticmethod
    def _load(file):
        with open(file) as config_file:
            result = config_file.read()
            result = result.strip()
        if file.endswith('.json'):
            result = json.loads(result)
        return result

    @staticmethod
    def _get_path(file):
        path_list = Config._get_env_path_list()
        file_paths = []
        for conf_dir in path_list:
            path = os.path.join(conf_dir, file)
            if os.path.exists(path):
                file_paths.append(path)
        return file_paths

    @staticmethod
    def _get_env_path_list():
        if Config.config_paths:
            return Config.config_paths

        Config.config_paths = Config._get_env_config_path().split(os.pathsep)
        Config.config_paths.sort(key=len)
        path = os.path.join(Config.config_paths[0], 'local')
        if os.path.exists(path):
            Config.config_paths.append(path)

        return Config.config_paths

    @staticmethod
    def _get_env_config_path():
        config_path = os.environ.get('CONFIG_PATH', None)
        if not config_path:
            raise NameError('Environment variable CONFIG_PATH not exist or is empty!')

        return config_path

    @staticmethod
    def _merge_config(config1, config2):
        if isinstance(config1, dict) and isinstance(config2, dict):
            return dict(Config._deep_update(config1, config2))
        if isinstance(config1, str) and isinstance(config2, str):
            return "\n".join([config1, config2])
        raise TypeError('You try to merge configs of different types: {config1} and {config2}'.format(
            config1=type(config1),
            config2=type(config2)
        ))

    @staticmethod
    def _deep_update(dict1, dict2):
        for k in set(dict1.keys()).union(dict2.keys()):
            if k in dict1 and k in dict2:
                if isinstance(dict1[k], dict) and isinstance(dict2[k], dict):
                    yield (k, dict(Config._deep_update(dict1[k], dict2[k])))
                else:
                    yield (k, dict2[k])
            elif k in dict1:
                yield (k, dict1[k])
            else:
                yield (k, dict2[k])
