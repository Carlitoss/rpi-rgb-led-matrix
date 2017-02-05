#!/usr/bin/env python
# Display a runtext with double-buffering.
import requests
import os
from samplebase import SampleBase
from rgbmatrix import graphics
from dotenv import Dotenv
import time

class RunText(SampleBase):
    def __init__(self, branch, branch_status, repeat_times, *args, **kwargs):
        super(RunText, self).__init__(*args, **kwargs)
        # self.parser.add_argument("-t", "--text", help="The text to scroll on the RGB LED panel", default="Build stat")
        # self.parser.add_argument("-t2", "--text2", help="The text to scroll on the RGB LED panel", default="Error")

        self.branch = branch
        self.branch_status = branch_status
        self.repeat_times = repeat_times

    def run(self):
        my_branch = self.branch
        my_status= self.branch_status
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        font.LoadFont("../../fonts/7x14.bdf")
        my_branch_color = graphics.Color(25, 205, 200)
        my_status_color = color_switcher_status(my_status)
        pos = offscreen_canvas.width

        # Efficiency improvement
        is_max_leng_calc = False
        max_len = 0
        print (is_max_leng_calc, max_len)

        while self.repeat_times:
            offscreen_canvas.Clear()
            if not is_max_leng_calc:
                len1 = graphics.DrawText(offscreen_canvas, font, pos, 12, my_branch_color, my_branch)
                len2 = graphics.DrawText(offscreen_canvas, font, pos, 30, my_status_color, my_status)
                max_len = len1 if len1 > len2 else len2
                is_max_leng_calc = True
            else:
                graphics.DrawText(offscreen_canvas, font, pos, 12, my_branch_color, my_branch)
                graphics.DrawText(offscreen_canvas, font, pos, 30, my_status_color, my_status)

                pos -= 1
                if pos + max_len < 0:
                    pos = offscreen_canvas.width
                    self.repeat_times -= 1

                time.sleep(0.02)
                offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)

        time.sleep(0.5)
        offscreen_canvas.Clear()


class ShowText(SampleBase):
    def __init__(self, branch, branch_status, delay_time, *args, **kwargs):
        super(ShowText, self).__init__(*args, **kwargs)

        self.branch = branch
        self.branch_status = branch_status
        self.delay_time = delay_time

    def run(self):
        canvas = self.matrix
        font = graphics.Font()
        font.LoadFont("../../fonts/7x14.bdf")
        my_branch_color = graphics.Color(25, 205, 200)
        my_status_color = color_switcher_status(self.branch_status)
        graphics.DrawText(canvas, font, 10, 12, my_branch_color, self.branch)
        graphics.DrawText(canvas, font, 0, 30, my_status_color, self.branch_status)
        time.sleep(self.delay_time)


def color_switcher_status(argument):
    switcher = {
        'success': graphics.Color(0, 254, 0),
        'failed': graphics.Color(254, 0, 0)
    }
    return switcher.get(argument, graphics.Color(25, 205, 200))

# Main function
if __name__ == "__main__":
    dotenv = Dotenv('../.env')
    os.environ.update(dotenv)
    payload = {'circle-token': os.getenv('CIRCLE_API_TOKEN', 'NO API TOKEN FOUND'), 'limit': '1'}
    r = requests.get('https://circleci.com/api/v1.1/recent-builds', params=payload)
    response = r.json()
    print response[0]['branch'], response[0]['status']
    run_text = RunText(response[0]['branch'], response[0]['status'], 3)
    if not run_text.process():
        show_text = ShowText(response[0]['branch'], response[0]['status'], 15)
        if not show_text.process():
            show_text.print_help()
        run_text.print_help()
