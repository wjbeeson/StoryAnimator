import sys                                          # System bindings
import cv2                                         # OpenCV bindings
import numpy as np


class ColorAnalyser():
    def __init__(self, src, debug=False):

        def rgb_to_int(rgb):
            # rgb is a tuple of three integers between 0 and 255
            # representing the red, green and blue components of a color
            # int is a single integer between 0 and 16777215
            # representing the same color in hexadecimal format
            # for example, rgb = (255, 0, 0) corresponds to int = 16711680
            # the formula to convert rgb to int is:
            # int = red * 65536 + green * 256 + blue
            red, green, blue = rgb  # unpack the tuple into three variables
            return red * 65536 + green * 256 + blue  # return the int value


        def count_colors():
            # Splits image Mat into 3 color channels in individual 2D arrays
            (channel_b, channel_g, channel_r) = cv2.split(self.src)

            # Flattens the 2D single channel array so as to make it easier to iterate over it
            channel_b = channel_b.flatten()
            channel_g = channel_g.flatten()  # ""
            channel_r = channel_r.flatten()  # ""

            for i in range(len(channel_b)):
                RGB = "(" + str(channel_r[i]) + "," + \
                      str(channel_g[i]) + "," + str(channel_b[i]) + ")"
                if RGB in self.colors_count:
                    self.colors_count[RGB] += 1
                else:
                    self.colors_count[RGB] = 1

            print("Colours counted")

        def get_mode():
            def convert_rgb_to_hex():
                split = self.background_rgb[1:len(self.background_rgb) - 1].split(",")
                red = int(split[0])
                green = int(split[1])
                blue = int(split[2])
                self.background_hex = '#{:02x}{:02x}{:02x}'.format(red, green, blue)


            # Sorts dictionary by value
            sorted_dict = sorted(self.colors_count, key=self.colors_count.__getitem__)
            if self.debug:
                for keys in sorted_dict:
                    # Prints 'key: value'
                    print(keys, ": ", self.colors_count[keys])
            mode = sorted_dict[len(sorted_dict) - 1]
            self.background_rgb = mode
            convert_rgb_to_hex()

        def pick_foreground():
            split = self.background_rgb[1:len(self.background_rgb) - 1].split(",")
            red = int(split[0])
            green = int(split[1])
            blue = int(split[2])
            if (red * 0.299 + green * 0.587 + blue * 0.114) > 186:
                self.foreground_hex = "000000"
            else:
                self.foreground_hex = "ffffff"

        # Empty dictionary container to hold the colour frequencies
        self.colors_count = {}
        # Global debug value
        self.debug = debug
        # Global background color
        self.background_rgb = None
        # Global background color
        self.background_hex = None
        # Global foreground color
        self.foreground_hex = None
 #       img = cv2.imread(imageLoc)  # Reads in image source
 #       self.src = img[ymin:ymax, xmin:xmax]  # Crops image source to the relevant area
        self.src = src
        if debug:
            cv2.imshow("cropped", self.src)
            cv2.waitKey()
        count_colors()
        get_mode()
        pick_foreground()

    def get_hex(self):
        if self.debug:
            print(f"Background: {self.background_hex}")
            print(f"Foreground: {self.foreground_hex}")
        return self.background_hex, self.foreground_hex

# # Example Code for how to use class
# img_loc = r"C:\Users\fjbee\PycharmProjects\Apollo\memes\Text Chat\Do_You_Wanna_Go_To_Target.png"
# xmin = 195
# ymin = 127
# xmax = 597
# ymax = 546
# debug = True  # shows the area where the background color is being extracted from w/ print statements
# background = ColorAnalyser(img_loc, xmin, ymin, xmax, ymax, debug)
# background_hex, foreground_hex = background.get_hex()
