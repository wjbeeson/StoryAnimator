import dto
import apollo_config as config

# number of speaker elements to create
SPEAKER_COUNT = 4

def memeify( raw_filename, overwite=False):

    #
    # create meme and header
    #

    meme = dto.Meme()
    meme.header = dto.Meme.Header()
    meme.header.state = dto.StateType.CREATED
    meme.header.speakers = dto.Meme.Speakers()
    meme.sequential = dto.Meme.Sequential()
    meme.sequential.preferred_axis = dto.OrientationType.PORTRAIT

    voices = config.MEMEIFY_DEFAULT_VOICES.split(",")

    for i in range(SPEAKER_COUNT):
        speaker = dto.Meme.Header.Speakers.Speaker(voice=voices[0])
        speaker.text_properties = dto.FontType()
        speaker.avatar_filename = ""
        meme.header.speakers.append(speaker)

    #
    # i'm currently expressing story memes as a single panel with one caption element per
    # paragraph.  an alternate approach would be one panel per paragraph
    #

    panel = dto.PanelType(xmin=0,xmax=0,ymin=0,ymax=0)
    panel

    #
    # create a caption element for each paragraph of the raw text
    #

    with open( raw_filename, "r", encoding="utf-8") as f:
        # split into paragraphs, dropping repeated linefeeds e.g. \n\n \n\n\n etc
        text = [para for para in f.read().split('\n') if para != '']





