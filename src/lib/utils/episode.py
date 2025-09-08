from dataclasses import asdict, dataclass
import re
from typing import List, Set
from enum import Enum

from pydantic import BaseModel, Field


@dataclass
class EpisodeMeta:
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
    NEW = "new"
    CHAR = "char"
    ROMANCE = "romance"
    BO = "bo"
    FBI = "fbi"
    MK = "mk"
    PAST = "past"
    HH = "hh"
    DB = "db"
    DC = "dc"
    MKO = "mko"


@dataclass
class Episode:
    season: int
    index_jpn: str
    index_int: str
    episode: EpisodeMeta
    date_jpn: str
    date_eng: str
    plots: Set[Plot]
    manga_source: str
    is_tv_original: bool
    next_hint: str

    def __str__(self) -> str:
        return f'{self.season} | {self.index_jpn} | {self.index_int} | {self.episode.label} | {self.date_jpn} | {self.date_jpn} | {self.date_eng} | {self.plots} | {self.manga_source} | {self.is_tv_original} | {self.next_hint}'

    def get_dict(self):
        return asdict(self)


class FilterParams(BaseModel):
    model_config = {"extra": "forbid"}

    filter: List[str] = Field([], max_length=10)
    plot: List[Plot] = Field([], max_length=10)
    season: List[int] = Field([], max_length=10)
    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)


# table_pattern = re.compile(r"<h3><span.*?>(.*?)</span></h3>.*?<tbody.*?><tr>\s*?<th.+?</th></tr>(.*?)</tbody>", re.DOTALL)
table_pattern = re.compile(r"(<h3>.*?</table>)", re.DOTALL)
table_header_pattern = re.compile(r"<h3><span.*?>(.*?)</span></h3>")
table_header_extractor_pattern = re.compile(r"Season (\d+?) - Episodes (\d+?)-(.+)")
table_content_pattern = re.compile(r"<tbody.*?><tr>\s*?<th.+?</th></tr>\s*(.*?)\s*</tbody>", re.DOTALL)
row_pattern = re.compile(r"<tr>(?P<rowdata>.*?)</tr>", re.DOTALL)
data_pattern = re.compile(r"<td.*?>(.*?)</td>\s*?", re.DOTALL)
episode_pattern = re.compile(r"<a\s*?href=\"(.*?)\"\s*?title=\"(.*?)\">(.*?)</a>")
plot_pattern = re.compile(r"<img.*?src=\".*?/Plot-(.*?)\..*?\".*?>")
source_tv_original_pattern = re.compile(r".*?<b>TV Original</b>.*?")


def extract_tables(page_html: str, table_pattern: re.Pattern[str], table_header_pattern: re.Pattern[str], table_header_extractor_pattern: re.Pattern[str], table_content_pattern: re.Pattern[str], filter_patterns: List[re.Pattern[str]]):
    tables_unformatted = re.findall(table_pattern, page_html)
    # print(f"found {len(tables_unformatted)} tables")
    tables: List[Table] = []
    for unformatted in tables_unformatted:
        filter_violation = False
        for pattern in filter_patterns:
            if not re.search(pattern, unformatted):
                filter_violation = True
                break
        if filter_violation:
            continue

        header_match = re.search(table_header_pattern, unformatted)
        content_match = re.search(table_content_pattern, unformatted)
        header_str = header_match.group(1).strip() if header_match else ""
        content_str =  content_match.group(1).strip() if content_match else ""

        is_season = bool(header_match)
        is_airing = False

        header_extracted = re.findall(table_header_extractor_pattern, header_str)
        if len(header_extracted) == 0:
            season = 0
            start_ep = 0
            end_ep = 0
            is_season = False
        else:
            season = int(header_extracted[0][0])
            start_ep = int(header_extracted[0][1])
            end_ep = 0
            # for ongoing season, end_ep will be `present`
            if header_extracted[0][2] != 'present':
                is_airing = False
                end_ep = int(header_extracted[0][2])
        tables.append(Table(is_season, is_airing, season, start_ep, end_ep, header_str, content_str))

    return tables


def extract_row_datas(table: Table, row_data_pattern: re.Pattern[str], filter_patterns: List[re.Pattern[str]]):
    episodes: List[Episode] = []

    rows = re.findall(row_pattern, table.html_table)
    # print(f"{str(table)} - found {len(rows)} rows")
    # print('\n'.join(rows))

    for row in rows:
        filter_violation = False
        for pattern in filter_patterns:
            if not re.search(pattern, row):
                filter_violation = True
                break
        if filter_violation:
            continue

        row_data_unformatted = re.findall(row_data_pattern, row)

        season = table.season
        index_jpn = row_data_unformatted[0].strip()
        index_int = row_data_unformatted[1].strip()
        episode_unformatted = re.findall(episode_pattern, row_data_unformatted[2])
        if len(episode_unformatted) == 0:
            episode_meta = EpisodeMeta('', row_data_unformatted[2], row_data_unformatted[2])
        else:
            episode_meta_link = episode_unformatted[0][0].strip()
            episode_meta_title = episode_unformatted[0][1].strip()
            episode_meta_label = episode_unformatted[0][2].strip()
            episode_meta = EpisodeMeta(episode_meta_link, episode_meta_title, episode_meta_label)
        date_jpn = row_data_unformatted[3].strip()
        # date_jpn_datetime = time.strptime(date_jpn, "%B %d, %Y")
        date_eng = row_data_unformatted[4].strip()
        # date_eng_datetime = time.strptime(date_eng, "%B %d, %Y")
        plot_unformatted = re.findall(plot_pattern, row_data_unformatted[5])
        plots = set((map(lambda plot_string: Plot[plot_string.upper()], plot_unformatted)))
        manga_source = row_data_unformatted[6].strip()
        is_tv_original = True if re.match(source_tv_original_pattern, manga_source) else False
        next_hint = row_data_unformatted[7].strip()

        episode = Episode(season, index_jpn, index_int, episode_meta, date_jpn, date_eng, plots, manga_source, is_tv_original, next_hint)
        episodes.append(episode)

    return episodes


def extract_episodes(page_html: str, filter_params: FilterParams) -> List[Episode]:
    table_filter_patterns: List[re.Pattern[str]] = []
    row_filter_patterns: List[re.Pattern[str]] = []
    if filter_params.filter:
        # filter OR
        # str_filter_pattern = re.compile(fr"<td.*?>.*?(?:{'|'.join(filter_params.filter)}).*?</td>", re.IGNORECASE)
        # table_filter_patterns.append(str_filter_pattern)
        # row_filter_patterns.append(str_filter_pattern)

        # filter AND
        str_filter_patterns = [re.compile(fr"<td.*?>.*?{re.escape(f)}.*?</td>", re.IGNORECASE) for f in filter_params.filter]
        table_filter_patterns.extend(str_filter_patterns)
        row_filter_patterns.extend(str_filter_patterns)

    if filter_params.season:
        season_filter_pattern = re.compile(fr"<h3><span.*?>Season (?:{'|'.join(map(str, filter_params.season))}) - Episodes.*?</span></h3>")
        table_filter_patterns.append(season_filter_pattern)

    if filter_params.plot:
        plot_filter_pattern = re.compile(fr"<img.*?src=\".*?Plot-(?:{'|'.join(map(lambda p: p.name, filter_params.plot))})\..*?\".*?>", re.IGNORECASE)
        row_filter_patterns.append(plot_filter_pattern)

    tables: List[Table] = extract_tables(page_html, table_pattern, table_header_pattern, table_header_extractor_pattern, table_content_pattern, table_filter_patterns)

    episodes: List[Episode] = []
    for table in tables:
        episodes.extend(extract_row_datas(table, data_pattern, row_filter_patterns))

    return episodes


def extract_episodes_asdict(page_html: str, filter_params: FilterParams):
    row_datas = extract_episodes(page_html, filter_params)
    return map(asdict, row_datas)


# wikipage = ''

# with open('/home/phuwit/Programming/CanYouRegMyEx-Backend/Anime - Detective Conan Wiki.html', 'r') as f:
#     wikipage = f.read()

# row_datas = extract_episodes(wikipage, FilterParams(filter=[], plot=[], season=[1], limit=100, offset=0))
# # row_dicts = list(extract_episodes_asdict(wikipage, FilterParams(filter=['shinkansen'], plot=[Plot.CHAR], season=[1], limit=100, offset=0)))

# print('\n\n'.join(map(str, row_datas)))
# # print(row_dicts)
