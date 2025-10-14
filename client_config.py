import json
import os


def load_server_config():
    config_file = "server_config.json"

    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, config_file)

    if not os.path.exists(config_path):
        config_path = config_file

    if not os.path.exists(config_path):
        default_config = {
            "host": "shinkansen.proxy.rlwy.net",
            "port": 20565
        }
        try:
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"Created {config_file} with default settings")
        except Exception as e:
            print(f"Warning: Could not create {config_file}: {e}")
            return default_config['host'], default_config['port']

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config.get('host', '127.0.0.1'), config.get('port', 5000)
    except json.JSONDecodeError:
        print(f"Error: {config_file} is not valid JSON. Using defaults (127.0.0.1:5000)")
        return '127.0.0.1', 5000
