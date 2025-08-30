from flask import request

def handler():
    body = request.json

    color1 = body["color1"]
    color2 = body["color2"]

    d = { "ratio": getContrastRatio(color1, color2) }

    return d

expected_body = {
    "color1": {
        "red": 0,
        "green": 0,
        "blue": 0
    },
    "color2": {
        "red": 0,
        "green": 0,
        "blue": 0
    }
}

def pow(base, exponent):
    pass

class Accessability:
    def __init__(self, html):
        self.html = html

def getContrastRatio(color1, color2):
    def getLuminance(red, green, blue):
        RED_CONST = 0.2126
        GREEN_CONST = 0.7152
        BLUE_CONST = 0.0722
        GAMMA = 2.4
        calculate_luminance = (
            lambda scale:
                lambda determiner:
                    lambda val:
                        determiner(scale(val))
        )(lambda _: _ / 255)(lambda _ : _ / 12.92 if _ <= 0.3928 else (((_ + 0.055) / 1.055) ** GAMMA))
        scaled_colors = list(map(calculate_luminance, [red, green, blue]))
        return scaled_colors[0] * RED_CONST + scaled_colors[1] * GREEN_CONST + scaled_colors[2] * BLUE_CONST


    luminance1 = getLuminance(**color1)
    luminance2 = getLuminance(**color2)

    minium = min(luminance1, luminance2)
    maximum = max(luminance1, luminance2)

    return (maximum + 0.05) / (minium + 0.05)