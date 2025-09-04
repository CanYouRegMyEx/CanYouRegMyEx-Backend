import re
from typing import List, Set
from enum import Enum, auto


class Episode:
    def __init__(self, link: str, title: str, label: str) -> None:
        self.link = link
        self.title = title
        self.label = label


class Table:
    def __init__(self, is_season: bool, is_airing: bool, season: int, start_ep: int, end_ep: int, header: str, html_table: str) -> None:
        self.is_season = is_season
        self.is_airing = is_airing
        self.season = season
        self.start_ep = start_ep
        self.end_ep = end_ep
        self.header = header
        self.html_table = html_table

    def __str__(self) -> str:
        return f"Table: S{self.season} ({self.start_ep}-{self.end_ep}) [{self.header}]"


class Plot(Enum):
    NEW = auto()
    CHAR = auto()
    ROMANCE = auto()
    BO = auto()
    FBI = auto()
    MK = auto()
    PAST = auto()
    HH = auto()
    DB = auto()
    DC = auto()
    MKO = auto()


class RowData:
    def  __init__(self, index_jpn: str, index_int: str, episode: Episode, date_jpn: str, date_eng: str, plots: Set[Plot], manga_source: str, next_hint: str) -> None:
        self.index_jpn = index_jpn
        self.index_int = index_int
        self.episode = episode
        self.date_jpn = date_jpn
        self.date_eng = date_eng
        self.plots = plots
        self.manga_source = manga_source
        self.next_hint = next_hint

    def __str__(self) -> str:
        return f'{self.index_jpn} | {self.index_int} | {self.episode.label} | {self.date_jpn} | {self.date_jpn} | {self.date_eng} | {self.plots} | {self.manga_source} | {self.next_hint}'


table_pattern = re.compile(r"<h3><span.*?>(.*?)</span></h3>.*?<tbody.*?><tr>\s*?<th.+?</th></tr>(.*?)</tbody>", re.DOTALL)
table_header_pattern = re.compile(r"Season (\d+?) - Episodes (\d+?)-(.+)")
row_pattern = re.compile(r"<tr>(?P<rowdata>.*?)</tr>", re.DOTALL)
data_pattern = re.compile(r"<td.*?>(.*?)</td>\s*?", re.DOTALL)
episode_pattern = re.compile(r"<a\s*?href=\"(.*?)\"\s*?title=\"(.*?)\">(.*?)</a>")
plot_pattern = re.compile(r"<img.*?src=\".*?/Plot-(.*?)\..*?\".*?>")


def extract_links(test_string: str, filter: str | None = None) -> List[RowData]:
    filter_pattern: None | re.Pattern[str] = None
    if filter:
        filter_pattern = re.compile(fr"<td.*?>.*?{re.escape(filter)}.*?</td>", re.IGNORECASE)

    tables_unformatted = re.findall(table_pattern, test_string)
    print(f"found {len(tables_unformatted)} tables")
    tables: List[Table] = []
    for unformatted in tables_unformatted:
        header = unformatted[0]
        html_table = unformatted[1]
        if filter_pattern and not re.search(filter_pattern, html_table):
            continue

        is_season = True
        is_airing = False

        header_unformatted = re.findall(table_header_pattern, header)
        if len(header_unformatted) == 0:
            season = 0
            start_ep = 0
            end_ep = 0
            is_season = False
        else:
            season = int(header_unformatted[0][0])
            start_ep = int(header_unformatted[0][1])
            end_ep = 0
            # for ongoing season, end_ep will be `present`
            if header_unformatted[0][2] != 'present':
                is_airing = False
                end_ep = int(header_unformatted[0][2])
        tables.append(Table(is_season, is_airing, season, start_ep, end_ep, header, html_table))

    # print("\n".join(map(str, tables)))

    row_datas: List[RowData] = []

    for table in tables:

        rows = re.findall(row_pattern, table.html_table)
        print(f"{str(table)} - found {len(rows)} rows")
        # print('\n'.join(rows))

        for idx, row in enumerate(rows):
            if filter_pattern and not re.search(filter_pattern, row):
                continue
            row_data_unformatted = re.findall(data_pattern, row)

            index_jpn = row_data_unformatted[0]
            index_int = row_data_unformatted[1]
            episode_unformatted = re.findall(episode_pattern, row_data_unformatted[2])
            if len(episode_unformatted) == 0:
                episode = Episode('', row_data_unformatted[2], row_data_unformatted[2])
            else:
                episode_link = episode_unformatted[0][0]
                episode_title = episode_unformatted[0][1]
                episode_label = episode_unformatted[0][2]
                episode = Episode(episode_link, episode_title, episode_label)
            date_jpn = row_data_unformatted[3]
            date_eng = row_data_unformatted[4]
            plot_unformatted = re.findall(plot_pattern, row_data_unformatted[5])
            plots = set((map(lambda plot_string: Plot[plot_string.upper()], plot_unformatted)))
            manga_source = row_data_unformatted[6]
            next_hint = row_data_unformatted[7]

            row_data = RowData(index_jpn, index_int, episode, date_jpn, date_eng, plots, manga_source, next_hint)
            row_datas.append(row_data)
            print(f"row #{idx}: {row_data}")

            # print(f"row {idx} has {len(row_data_unformatted)} datas")
            # print('\t'.join(map(lambda s: s.encode('unicode_escape').decode("utf-8"), row_data_unformatted)))

    return row_datas


# wikipage = ''

# with open('./Anime - Detective Conan Wiki.html', 'r') as f:
#     wikipage = f.read()

# print('\n'.join((map(str, extract_links(wikipage, 'shinkan')))))