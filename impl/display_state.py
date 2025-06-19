class DisplayState:
    def __init__(self):
        self.current_app_label = "Time"  # Default app index
        self.custom_text = ""

# Singleton instance to be imported elsewhere
display_state = DisplayState()