from flask import request
from bs4 import BeautifulSoup

import re
from PIL import ImageColor

def handler():

    body = request.json

    acc = AccessibilityChecker()

    d = acc.check(body["html"])

    return d

expected_body = {
    "html": ""
}

def pow(base, exponent):
    return base ** exponent

class AccessibilityChecker:
    def __init__(self):
        self.issues = []
        self.soup = None

    def check(self, html: str) -> dict:
        self.issues = []
        self.soup = BeautifulSoup(html, 'html5lib')
        self.checkLang()
        self.checkTitle()
        self.checkImages()
        self.checkHeadings()
        self.checkContrast()
        self.checkLinks()

        return {
            "issues": self.issues,
            "passed": len(self.issues) == 0
        }

    def reportIssue(self, rule_id, message, tag=None):
        self.issues.append({
            "ruleId": rule_id,
            "message": message,
            "element": tag.name if tag else None,
            "selector": self.getSelector(tag) if tag else None,
            "codeSnippet": str(tag) if tag else None
        })

    def getSelector(self, tag):
        path = []
        current = tag
        while current and current.name != '[document]':
            name = current.name
            if current.get('id'):
                name += f"#{current['id']}"
            elif current.get('class'):
                classes = ".".join(current['class'])
                name += f".{classes}"
            path.insert(0, name)
            current = current.parent
        return " > ".join(path)

    def checkLang(self):
        html_tag = self.soup.find('html')
        if not html_tag or not html_tag.get('lang'):
            self.reportIssue('DOC_LANG_MISSING', "Missing or empty 'lang' attribute on <html>.", html_tag)

    def checkTitle(self):
        title_tag = self.soup.find('title')
        if not title_tag or not title_tag.text.strip():
            self.reportIssue('DOC_TITLE_MISSING', "Missing or empty <title> tag.", title_tag)

    def checkImages(self):
        for img in self.soup.find_all('img'):
            alt = img.get('alt')
            if alt is None:
                self.reportIssue('IMG_ALT_MISSING', "<img> tag missing 'alt' attribute.", img)
            elif len(alt) > 120:
                self.reportIssue('IMG_ALT_LENGTH', f"<img> alt text too long ({len(alt)} characters), it should be less than 120 characters.", img)

    def checkHeadings(self):
        headings = self.soup.find_all(re.compile('^h[1-6]$'))
        h1_count = sum(1 for h in headings if h.name == 'h1')
        if h1_count != 1:
            tag = next((h for h in headings if h.name == 'h1'), headings[0] if headings else None)
            self.reportIssue('HEADING_MULTIPLE_H1', f"Document should contain exactly one <h1>. Found {h1_count}.", tag)

        last_level = 0
        for heading in headings:
            level = int(heading.name[1])
            if last_level and level > last_level + 1:
                self.reportIssue('HEADING_ORDER', f"Skipped heading level: {heading.name} after h{last_level}.", heading)
            last_level = level

    def parseColors(self, style):
        color_match = re.search(r'color\s*:\s*([^;]+)', style, re.IGNORECASE)
        bg_match = re.search(r'background-color\s*:\s*([^;]+)', style, re.IGNORECASE)

        color = color_match.group(1).strip() if color_match else '#000'
        bg = bg_match.group(1).strip() if bg_match else '#fff'

        try:
            color_rgb = rgb(*ImageColor.getrgb(color))
            bg_rgb = rgb(*ImageColor.getrgb(bg))
            return color_rgb, bg_rgb
        except:
            return None, None

    def isLargeText(self, tag):
        style = tag.get('style', '')
        font_size = re.search(r'font-size\s*:\s*(\d+)px', style)
        if font_size:
            px = int(font_size.group(1))
            return px >= 18
        return False

    def checkContrast(self):
        for tag in self.soup.find_all(text=True):
            parent = tag.parent
            if parent.name in ['script', 'style']:
                continue
            style = parent.get('style', '')
            fg, bg = self.parseColors(style)
            if fg and bg:
                try:
                    contrast_ratio = self.ratio(fg, bg)
                    is_large = self.isLargeText(parent)
                    required = 3.0 if is_large else 4.5
                    if contrast_ratio < required:
                        snippet = tag.strip().replace('\n', ' ')[:30]
                        self.reportIssue(
                            'COLOR_CONTRAST',
                            f"Low contrast ({contrast_ratio:.2f}:1) for text: '{snippet}...'",
                            parent
                        )
                except:
                    continue
    
    def ratio(self, color1, color2):
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

    def checkLinks(self):
        generic_phrases = {'click here', 'read more', 'more', 'here', 'link', 'learn more'}
        for link in self.soup.find_all('a'):
            text = link.get_text().strip().lower()
            if text in generic_phrases:
                self.reportIssue(
                    'LINK_GENERIC_TEXT',
                    f"Link text '{text}' is too generic. Use more descriptive text.",
                    link
                )

    def __init__(self):
        self.issues = []

    def check(self, html: str) -> dict:
        self.issues = []
        soup = BeautifulSoup(html, 'html5lib')

        self.checkLang(soup)
        self.checkTitle(soup)
        self.checkImages(soup)
        self.checkHeadings(soup)
        self.checkContrast(soup)

        return {
            'issues': self.issues,
            'passed': len(self.issues) == 0
        }

    def checkLang(self, soup):
        html_tag = soup.find('html')
        if not html_tag or not html_tag.get('lang'):
            self.issues.append("Missing or empty 'lang' attribute on <html>.")

    def checkTitle(self, soup):
        title_tag = soup.find('title')
        if not title_tag or not title_tag.text.strip():
            self.issues.append("Missing or empty <title> tag.")

    def checkImages(self, soup):
        for img in soup.find_all('img'):
            alt = img.get('alt')
            if alt is None:
                self.issues.append("<img> tag missing 'alt' attribute.")
            elif len(alt) > 120:
                self.issues.append(f"<img> alt text too long ({len(alt)} characters).")

    def checkHeadings(self, soup):
        headings = soup.find_all(re.compile('^h[1-6]$'))
        h1_count = sum(1 for h in headings if h.name == 'h1')
        if h1_count != 1:
            self.issues.append(f"Document should contain exactly one <h1>. Found {h1_count}.")

        last_level = 0
        for heading in headings:
            level = int(heading.name[1])
            if last_level and level > last_level + 1:
                self.issues.append(f"Skipped heading level: {heading.name} after h{last_level}.")
            last_level = level

    def parseColors(self, style):
        color_match = re.search(r'color\s*:\s*([^;]+)', style, re.IGNORECASE)
        bg_match = re.search(r'background-color\s*:\s*([^;]+)', style, re.IGNORECASE)

        color = color_match.group(1).strip() if color_match else '#000'
        bg = bg_match.group(1).strip() if bg_match else '#fff'

        try:
            color_rgb = rgb(*ImageColor.getrgb(color))
            bg_rgb = rgb(*ImageColor.getrgb(bg))
            return color_rgb, bg_rgb
        except:
            return None, None

    def isLargeText(self, tag):
        style = tag.get('style', '')
        font_size = re.search(r'font-size\s*:\s*(\d+)px', style)
        if font_size:
            px = int(font_size.group(1))
            return px >= 18
        return False

    def checkContrast(self, soup):
        for tag in soup.find_all(text=True):
            parent = tag.parent
            if parent.name in ['script', 'style']:
                continue
            style = parent.get('style', '')
            fg, bg = self.parseColors(style)
            if fg and bg:
                try:
                    contrast_ratio = ratio(fg, bg)
                    is_large = self.isLargeText(parent)
                    required_ratio = 3.0 if is_large else 4.5
                    if contrast_ratio < required_ratio:
                        snippet = tag.strip().replace('\n', ' ')[:30]
                        self.issues.append(
                            f"Low contrast ({contrast_ratio:.2f}:1) for text: '{snippet}...'"
                        )
                except:
                    continue

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
            )(lambda _: _ / 255)(lambda _ : _ / 12.92 if _ <= 0.3928 else pow((_ + 0.055) / 1.055, GAMMA))
            scaled_colors = list(map(calculate_luminance, [red, green, blue]))
            return scaled_colors[0] * RED_CONST + scaled_colors[1] * GREEN_CONST + scaled_colors[2] * BLUE_CONST


        luminance1 = getLuminance(**color1)
        luminance2 = getLuminance(**color2)

        minium = min(luminance1, luminance2)
        maximum = max(luminance1, luminance2)

        return (maximum + 0.05) / (minium + 0.05)