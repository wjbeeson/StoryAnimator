"""
An alternative text clip for Moviepy, relying on Gizeh instead of ImageMagick
Advantages:
- Super fast (20x faster)
- no need to install imagemagick
- full-vector graphic, no aliasing problems
- Easier font names
Disadvantages:
- Requires Cairo installed
- Doesnt support kerning (=letters spacing)
"""

try:
    import gizeh as gz
    import math
    from PIL import Image

    GIZEH_AVAILABLE = True
except ImportError:
    GIZEH_AVAILABLE = False
import numpy as np
from moviepy.editor import ImageClip

import forge.colors as colors

#
# this code requires a modification to gizeh\gizeh.py.
# replace the yshift calculation in gizeh.py:text:draw with the following:
#
# (ascent, descent, height, max_x_advance, max_y_advance) = ctx.font_extents()
# yshift = -xy[1] + height - descent
#

def dbg_show(img):
    i = Image.fromarray(img)
    i.show()

class GzTextClip(ImageClip):
    def _autocrop(self, np_img):
        """Return the numpy image without empty margins."""
        if len(np_img.shape) == 3:
            if np_img.shape[2] == 4:
                thresholded_img = np_img[:, :, 3]  # use the mask
            else:
                thresholded_img = np_img.max(axis=2)  # black margins
        zone_x = thresholded_img.max(axis=0).nonzero()[0]
        xmin, xmax = zone_x[0], zone_x[-1]
        zone_y = thresholded_img.max(axis=1).nonzero()[0]
        ymin, ymax = zone_y[0], zone_y[-1]


        # don't crop the top.  it makes it impossible to maintain stable vertical alignment of words
        # with different heights and descenders
        ymin = 0
        return np_img[:ymax+1,xmin:xmax+1]

        return np_img[ymin:ymax + 1, xmin:xmax + 1]

    def _text_clip(self,text, font_family, align='left',
                   font_weight='normal', font_slant='normal',
                   font_height=70, font_width=None,
                   interline=None, fill_color=(0, 0, 0),
                   stroke_color=(0, 0, 0), stroke_width=2,
                   bg_color=None):
        """Return an ImageClip displaying a text.

        Parameters
        ----------

        text
          Any text, possibly multiline

        font_family
          For instance 'Impact', 'Courier', whatever is installed
          on your machine.

        align
          Text alignment, either 'left', 'center', or 'right'.

        font_weight
          Either 'normal' or 'bold'.

        font_slant
          Either 'normal' or 'oblique'.

        font_height
          Eight of the font in pixels.

        font_width
          Maximal width of a character. This is only used to
          create a surface large enough for the text. By
          default it is equal to font_height. Increase this value
          if your text appears cropped horizontally.

        interline
          number of pixels between two lines. By default it will be

        stroke_width
          Width of the letters' stroke in pixels.

        stroke_color
          For instance (0,0,0) for black stroke or (255,255,255)
          for white.

        fill_color=(0,0,0),
          For instance (0,0,0) for black letters or (255,255,255)
          for white.

        bg_color
          The background color in RGB or RGBA, e.g. (255,100,230)
          (255,100,230, 128) for semi-transparent. If left to none,
          the background is fully transparent

        """

        if not GIZEH_AVAILABLE:
            raise ImportError("`text_clip` requires Gizeh installed.")

        stroke_color = np.array(stroke_color) / 255.0
        fill_color = np.array(fill_color) / 255.0
        if bg_color is not None:
            np.array(bg_color) / 255.0

        if font_width is None:
            font_width = font_height
        if interline is None:
            interline = 0.3 * font_height

        line_height = font_height + interline
        lines = text.splitlines()
        max_line = max(len(l) for l in lines)
        W = int(max_line * font_width + 2 * stroke_width)
        H = int(len(lines) * line_height + 2 * stroke_width)
        surface = gz.Surface(width=W, height=H, bg_color=bg_color)
        xpoint = {
            'center': W / 2,
            'left': stroke_width + 1,
            'right': W - stroke_width - 1
        }[align]
        for i, line in enumerate(lines):
            ypoint = (i + 1) * line_height
            text_element = gz.text(line, fontfamily=font_family, fontsize=100,
                                   h_align=align, v_align='top',
                                   xy=[xpoint, ypoint], fontslant=font_slant,
                                   stroke=stroke_color, stroke_width=stroke_width,
                                   fill=fill_color)

            text_element = text_element.scale(font_height/100)
            text_element.draw(surface)
        return self._autocrop(surface.get_npimage(transparent=True))

    def _create_gztext_clip( self, fontsize = None):

        return self._text_clip(
            text=self._txt,
            font_family=self._font,
            align='left',
            font_weight='normal',
            font_slant='normal',
            font_height= fontsize if fontsize else self._fontsize,
            font_width=None,
            interline=None,
            fill_color=self._color,
            stroke_color=self._stroke_color,
            stroke_width=self._stroke_width,
            bg_color=None
        )


    def __init__(self,
        txt,
        color,
        fontsize,
        font,
        stroke_color = None,
        stroke_width = None):

        self._txt = txt
        self._color = colors.color_to_rgb(color)
        self._fontsize = fontsize
        self._font = font
        self._stroke_color =  colors.color_to_rgb(stroke_color) if stroke_color else self._color
        self._stroke_width = stroke_width if stroke_width else 0

        img = self._create_gztext_clip()
        super().__init__(img)

    def resize(self, new_size):

        def make_clip(t):
            clip = ImageClip(self._create_gztext_clip(
                math.ceil(self._fontsize * new_size(t))))

            new_clip= self.fl(lambda gf, t: make_clip(t).img)
            new_clip.mask = clip.mask

            return new_clip



        if isinstance(new_size, (int, float)):
            fontsize = math.ceil(self._fontsize * new_size)
            img = self._create_gztext_clip( fontsize)

            # creating an ImageClip does whatever voodoo necessary to create the mask correctly
            img_clip = ImageClip(img)

            # this is how I create a new clip with the same position, duration etc, but using the new
            # img data
            new_clip =  self.fl_image( lambda f: img_clip.img)

            new_clip.mask = img_clip.mask

            return new_clip
        elif hasattr(new_size, "__call__"):
            # experimental code: there must be a more efficient way to do this
            fn_resize_clip = lambda t: ImageClip(self._create_gztext_clip(
                math.ceil(self._fontsize * new_size(t))))

            new_clip = self.fl( fl = lambda gf,t: fn_resize_clip(t).img )

            mask = self.fl( lambda gf, t: fn_resize_clip(t).mask.img)

            new_clip.mask = mask

            return new_clip


            #
            # fn_resize_clip = lambda t: ImageClip(self._create_gztext_clip(
            #     math.ceil(self._fontsize * new_size(t))))
            #
            # new_clip = self.fl( lambda gf,t: fn_resize_clip(t).img )
            #
            # mask = self.fl( lambda gf, t: fn_resize_clip(t).mask.img)
            #
            # new_clip.mask = mask
            #
            # return new_clip


