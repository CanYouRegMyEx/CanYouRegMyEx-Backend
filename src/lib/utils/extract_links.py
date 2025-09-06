from dataclasses import asdict, dataclass
import re
from typing import List, Set
from enum import Enum, auto


@dataclass
class Episode:
    link: str
    title: str
    label: str


@dataclass
class Table:
    is_season: bool
    is_airing: bool
    season: int
    start_ep: int
    end_ep: int
    header: str
    html_table: str

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


@dataclass
class RowData:
    index_jpn: str
    index_int: str
    episode: Episode
    date_jpn: str
    date_eng: str
    plots: Set[Plot]
    manga_source: str
    is_tv_original: bool
    next_hint: str

    def __str__(self) -> str:
        return f'{self.index_jpn} | {self.index_int} | {self.episode.label} | {self.date_jpn} | {self.date_jpn} | {self.date_eng} | {self.plots} | {self.manga_source} | {self.is_tv_original} | {self.next_hint}'

    def get_dict(self):
        return asdict(self)


table_pattern = re.compile(r"<h3><span.*?>(.*?)</span></h3>.*?<tbody.*?><tr>\s*?<th.+?</th></tr>(.*?)</tbody>", re.DOTALL)
table_header_pattern = re.compile(r"Season (\d+?) - Episodes (\d+?)-(.+)")
row_pattern = re.compile(r"<tr>(?P<rowdata>.*?)</tr>", re.DOTALL)
data_pattern = re.compile(r"<td.*?>(.*?)</td>\s*?", re.DOTALL)
episode_pattern = re.compile(r"<a\s*?href=\"(.*?)\"\s*?title=\"(.*?)\">(.*?)</a>")
plot_pattern = re.compile(r"<img.*?src=\".*?/Plot-(.*?)\..*?\".*?>")
source_tv_original_pattern = re.compile(r".*?<b>TV Original</b>.*?")


def extract_tables(page_html: str, table_pattern: re.Pattern[str], filter_pattern: re.Pattern[str] | None):
    tables_unformatted = re.findall(table_pattern, page_html)
    # print(f"found {len(tables_unformatted)} tables")
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

    return tables


def extract_row_datas(table: Table, row_data_pattern: re.Pattern[str], filter_pattern: re.Pattern[str] | None):
    row_datas: List[RowData] = []

    rows = re.findall(row_pattern, table.html_table)
    # print(f"{str(table)} - found {len(rows)} rows")
    # print('\n'.join(rows))

    for row in rows:
        if filter_pattern and not re.search(filter_pattern, row):
            continue
        row_data_unformatted = re.findall(data_pattern, row)

        index_jpn = row_data_unformatted[0].strip()
        index_int = row_data_unformatted[1].strip()
        episode_unformatted = re.findall(episode_pattern, row_data_unformatted[2])
        if len(episode_unformatted) == 0:
            episode = Episode('', row_data_unformatted[2], row_data_unformatted[2])
        else:
            episode_link = episode_unformatted[0][0].strip()
            episode_title = episode_unformatted[0][1].strip()
            episode_label = episode_unformatted[0][2].strip()
            episode = Episode(episode_link, episode_title, episode_label)
        date_jpn = row_data_unformatted[3].strip()
        # date_jpn_datetime = time.strptime(date_jpn, "%B %d, %Y")
        date_eng = row_data_unformatted[4].strip()
        # date_eng_datetime = time.strptime(date_eng, "%B %d, %Y")
        plot_unformatted = re.findall(plot_pattern, row_data_unformatted[5])
        plots = set((map(lambda plot_string: Plot[plot_string.upper()], plot_unformatted)))
        manga_source = row_data_unformatted[6].strip()
        is_tv_original = True if re.match(source_tv_original_pattern, manga_source) else False
        next_hint = row_data_unformatted[7].strip()

        row_data = RowData(index_jpn, index_int, episode, date_jpn, date_eng, plots, manga_source, is_tv_original, next_hint)
        row_datas.append(row_data)

    return row_datas


def extract_links(page_html: str, filter: str | None = None) -> List[RowData]:
    filter_pattern: None | re.Pattern[str] = None
    if filter:
        filter_pattern = re.compile(fr"<td.*?>.*?{re.escape(filter)}.*?</td>", re.IGNORECASE)

    tables: List[Table] = extract_tables(page_html, table_pattern, filter_pattern)

    row_datas: List[RowData] = []
    for table in tables:
        row_datas.extend(extract_row_datas(table, data_pattern, filter_pattern))

    return row_datas


def extract_links_asdict(page_html: str, filter: str | None = None):
    row_datas = extract_links(page_html, filter)
    return map(asdict, row_datas)


# wikipage = ''

# with open('/home/phuwit/Programming/CanYouRegMyEx-Backend/src/lib/utils/Anime - Detective Conan Wiki.html', 'r') as f:
#     wikipage = f.read()

# row_datas = extract_links(wikipage)
# row_dicts = list(extract_links_asdict(wikipage))

# print(row_datas)
# print(row_dicts)
