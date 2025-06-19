from PIL import Image, ImageDraw, ImageFont

def wrap_text(text, font, max_width, draw):
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        _, _, w, _ = draw.textbbox((0, 0), test_line, font = font)
        if w <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

class TextScreen:
    def __init__(self, config, shared_state, fullscreen):
        self.shared_state = shared_state
        self.font = ImageFont.truetype("fonts/tiny.otf", 10)  # Adjust as needed
        self.canvas_width = 64
        self.canvas_height = 64

    def generate(self):
        text = self.shared_state.custom_text or ""
        img = Image.new("RGB", (self.canvas_width, self.canvas_height), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        max_width = self.canvas_width - 4
        lines = wrap_text(text, self.font, max_width, draw)
        y = 0
        for line in lines:
            draw.text((2, y), line, font=self.font, fill=(255, 255, 0))
            y += draw.textbbox((0, 0), line, font=self.font)[3] + 2
            if y > self.canvas_height:
                break
        return img, True