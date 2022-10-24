from json import loads
from yaml import full_load


with open('config.yaml') as cfg_file:
    cfg = full_load(cfg_file)['bs_servers']


class Data:
    name = tuple(cfg['folders'].keys())[0]
    players_stats_file = (
        cfg['path'] +
        cfg['folders'][name] +
        cfg['players_stats_file']
    )

    @staticmethod
    def update(new_name: str) -> None:
        name = new_name
        players_stats_file = (
            cfg['path'] +
            cfg['folders'][name] +
            cfg['players_stats_file']
        )


def get_players_stats() -> dict:
    with open(Data.players_stats_file) as stats_file:
        return loads(stats_file.read())


def get_players_top() -> tuple:
    return tuple(map(
        lambda x: x[1],
        sorted(
            get_players_stats().items(),
            key=lambda x: x[1]['kills'],
            reverse=True
        )
    ))
