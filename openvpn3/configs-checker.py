import json
import time
import requests
import subprocess


def _get_configs() -> list[str]:
    completed_process = subprocess.run(['openvpn3', 'configs-list', '--json'], stdout=subprocess.PIPE, encoding='UTF-8')
    configs_dict = json.loads(completed_process.stdout)
    configs_values = list(configs_dict.values())
    return [c["name"] for c in configs_values]


def _vpn_shutdown(config_name: str):
    subprocess.run(
        ["openvpn3", "session-manage", "-c", config_name, "--disconnect"]
    )


def _vpn_start(config_name: str, timeout: int = 5):
    try:
        subprocess.run(
            ["openvpn3", "session-start", "-c", config_name],
            check=True,
            timeout=timeout
        )
    except Exception:
        _vpn_shutdown(config_name)


def _check_config_for_url(config_name: str, url: str) -> float | None:
    request_timeout = 3

    _vpn_start(config_name)
    start_time = time.time()
    try:
        response = requests.get(url, timeout=request_timeout)
    except Exception:
        _vpn_shutdown(config_name)
        return None
    if not response.ok:
        _vpn_shutdown(config_name)
        return None
    finish_time = time.time()
    _vpn_shutdown(config_name)
    return finish_time - start_time


def _check_configs_for_url(configs: list[str], url: str) -> str:
    current_best = None
    current_best_delay: float | None = None
    for config_name in configs:
        delay = _check_config_for_url(config_name, url)
        if not current_best_delay or current_best_delay > delay:
            current_best = config_name
            current_best_delay = delay
    return current_best


def main(url: str):
    configs = _get_configs()
    result = _check_configs_for_url(configs, url)
    print(result)


if __name__ == '__main__':
    main("https://chatgpt.com/")
