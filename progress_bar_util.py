class ProgressBar:
    def __init__(self, total_segment_count):
        self.total_segment_count = total_segment_count

    def update(self, current_completion):
        current_bars = round(current_completion * self.total_segment_count)
        print_bar = ""
        
        for bar in range(current_bars):
            print_bar += "█"

        for i in range(self.total_segment_count - current_bars):
            print_bar += "_"

        print(print_bar, end="\r")

    def end(self):
        print("")