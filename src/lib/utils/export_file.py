from lib.utils.extract_episode_list import extract_episodes_all, Plot
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List
import csv
import io
import json

def export_csv(page):
    episodes = extract_episodes_all(page)
    output = io.StringIO()
    writer = csv.writer(output)
    cols = ['Season', 'Title', 'Date Published (Japan)', 'Date Published (English)', 'Plots', 'Manga Source', 'TV Original', 'Next Hint']
    writer.writerow(cols)
    for episode in episodes:
        writer.writerow([episode.season, episode.episode.label, episode.date_jpn,
                        episode.date_eng, ' | '.join(list(map(lambda plot: plot.value, episode.plots))),episode.manga_source,
                        episode.is_tv_original, episode.next_hint])
    output.seek(0)
    return StreamingResponse(content=output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=export.csv"})

def export_json(page):
    episodes = extract_episodes_all(page)
    data = [
        {
            "Season": episode.season,
            "Title": episode.episode.label,
            "Date Published (Japan)": episode.date_jpn,
            "Date Published (English)": episode.date_eng,
            "Plots": [plot.value for plot in episode.plots],
            "Manga Source": episode.manga_source,
            "TV Original": episode.is_tv_original,
            "Next Hint": episode.next_hint
        }
        for episode in episodes
    ]

    json_str = json.dumps(data, indent=2, ensure_ascii=False)

    file_obj = io.BytesIO(json_str.encode("utf-8"))

    return StreamingResponse(
        file_obj,
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=export.json"}
    )