from pytube import YouTube
from datetime import timedelta
import innertube

def extract_transcript_params(next_data):
    engagement_panels = next_data["engagementPanels"]

    for engagement_panel in engagement_panels:
        engagement_panel_section = engagement_panel[
            "engagementPanelSectionListRenderer"
        ]

        if (
            engagement_panel_section.get("panelIdentifier")
            != "engagement-panel-searchable-transcript"
        ):
            continue

        return engagement_panel_section["content"]["continuationItemRenderer"][
            "continuationEndpoint"
        ]["getTranscriptEndpoint"]["params"]


def get_chapters(transcript):
    segments = transcript["actions"][0][
        "updateEngagementPanelAction"]["content"][
        "transcriptRenderer"]["content"][
        "transcriptSearchPanelRenderer"]["body"][
        "transcriptSegmentListRenderer"]["initialSegments"]
    
    chapters = []
    for segment in segments:
        if segment.get("transcriptSectionHeaderRenderer"):
            section = segment["transcriptSectionHeaderRenderer"]
            print(section)
            chapters.append(dict(
                start=float(section["startMs"]) / 1000.,
                end=float(section["endMs"]) / 1000.,
                label=section["snippet"]["simpleText"]
            ))
    return chapters 

yt = YouTube("https://www.youtube.com/watch?v=fgZq_rnT18Q") # edit for youtube link
print(yt.title)
it = innertube.InnerTube("WEB")
data = it.next(yt.video_id)
params = extract_transcript_params(data)
transcript = it.get_transcript(params)
chapters = get_chapters(transcript)

yt.streams.get_highest_resolution().download()
# give 5 minutes to download the mp4
import os
import time

time_to_wait = 300
time_counter = 0
while not os.path.exists('./*mp4'):
    time.sleep(1)
    time_counter += 1
    if time_counter > time_to_wait:break

# for chapter in yt.chapters:
#     fancy_start_tm = timedelta(seconds=chapter["timestamp"] / 1000.)
#     print(f"{fancy_start_tm} {chapter['label']}")

# call bash script to generate mp3 from mp4
from subprocess import call
rc = call('./mp42mp3.sh')

# give 5 minutes to convert to mp3
import os
import time

time_to_wait = 300
time_counter = 0
while not os.path.exists('./*mp3'):
    time.sleep(1)
    time_counter += 1
    if time_counter > time_to_wait:break

from pydub import AudioSegment
song = AudioSegment.from_mp3("./*.mp3") # edit to the source mp3 file

for x in chapters:
    t_start = x['start']*1000 # into milliseconds
    t_end = x['end']*1000 # into milliseconds
    new_song = song[t_start:t_end]
    new_song.export(f"./{x['label'].replace('/', '_')}.mp3", format="mp3")
