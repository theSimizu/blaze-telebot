from email import generator
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from time import sleep

class Blaze:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.start = datetime.timestamp(datetime.now())
        self.check_time = datetime.timestamp(datetime.now())
        self.driver.get("https://blaze.com/pt/games/double")

    def wait_elements(self, by, value):
        while True:
            sleep(1)
            elements = self.driver.find_elements(by, value)
            if len(elements) > 0:
                return elements

class BlazeDoubleCrawler(Blaze):
    def __init__(self):
        super().__init__()
        self.driver.get("https://blaze.com/pt/games/double")

    def get_boxes_list(self):
        last_boxes = self.wait_elements(By.CLASS_NAME, 'roulette-previous')[0]
        boxes = last_boxes.find_elements(By.CLASS_NAME, 'sm-box')[::-1]
        boxes = map(lambda box: box.get_dom_attribute("class").split(' ')[1], boxes)
        boxes = list(boxes)
        return boxes[-20:]

    def get_new_box(self):
        new_box_list = self.wait_elements(By.CLASS_NAME, 'roulette-previous')[0]
        new_boxes = new_box_list.find_elements(By.CLASS_NAME, 'sm-box')
        new_box = new_boxes[0].get_dom_attribute("class").split(' ')[1]
        return new_box

    def new_box_trigger(self):
        new = False
        while True:
            sleep(1)
            time_left = self.wait_elements(By.CLASS_NAME, 'time-left')[0]
            try:
                if 'girando' in time_left.text.lower():
                    new = True
                if 'blaze girou' in time_left.text.lower() and new:
                    return True
            except Exception as e:
                print('Error!!!')

    def check_boxes(self, current_boxes) -> bool:
        sleep(1)
        new_boxes = self.get_boxes_list()
        if current_boxes[-20:] == new_boxes[-20:]: return True 
        return False

    def run(self) -> generator:
        if self.new_box_trigger(): boxes = self.get_boxes_list()
        while True:
            if self.new_box_trigger():
                boxes.pop(0)
                boxes.append(self.get_new_box())
                if not self.check_boxes(boxes): boxes = self.get_boxes_list()
                yield boxes

if __name__ == '__main__':
    double = BlazeDoubleCrawler()
    double.run()