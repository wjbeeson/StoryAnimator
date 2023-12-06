import dto
import dto_utils
import apollo_config as config

from pathlib import Path

# number of speaker elements to create
SPEAKER_COUNT = 4

def memeify( raw_filename, overwrite=False):

    #
    # create meme and header
    #

    meme = dto.Meme.read( str(config.APOLLO_PATH / "config/blank.xml"))
    #
    # create a caption element for each paragraph of the raw text
    #

    with open( raw_filename, "r", encoding="utf-8") as f:
        # split into paragraphs, dropping repeated linefeeds e.g. \n\n \n\n\n etc
        text = [para.replace('\n','') for para in f.read().split('\n\n') if para != '']

    # remove sample content
    meme.panels[0].content.clear()

    # create caption content for each paragraph
    for para in text:
        caption_content = dto.CaptionContent(xmin=-1,ymin=-1,ymax=-1,xmax=-1,ocr=False,clean=dto.CleanMethod.NONE,text=para)
        content = dto.PanelType.Content( caption = caption_content, type=dto.ContentType.CAPTION)

        meme.panels[0].content.append(content)

    meme.write(str(Path(raw_filename).with_suffix(".meme")), overwrite)

