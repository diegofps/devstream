#!/usr/bin/env python3

from eye import Eye

import sys


class Program:

    def __init__(self):

        self.config_path = 'configs.json'
        self.id2label = {}
        self.eye = None
                
        self.new_model()

    def capture_screen(self):
        self.eye.capture_screen()

    def learn_region(self):
        region = self.eye.request_region('Select a region to train')
        name = input('\nRegionName> ')
        id = self.eye.learn(region)
        self.id2label[id] = name

    def search_region(self):
        options = [(str(k), v) for k,v in self.id2label.items()]
        option = self.pick_option(options)
        if option is not None:
            self.eye.find(int(option[0]))

    def export_as_base64(self):
        base64 = self.eye.exportAsBase64()
        print(base64)

    def import_from_base64(self):
        base64 = input('base64> ')
        self.eye = Eye(base64data=base64)

    def new_model(self):
        self.eye = Eye(configFilepath=self.config_path)
        self.id2label = {}

    def exit(self):
        sys.exit(0)

    def run(self):

        options = [
            ('1', 'Capture Screen', self.capture_screen),
            ('2', 'Learn Region', self.learn_region),
            ('3', 'Search Region', self.search_region),
            ('4', 'Export as base64', self.export_as_base64),
            ('5', 'Import from base64', self.import_from_base64),
            ('6', 'New model', self.new_model),
            ('0', 'Exit', self.exit)
        ]

        while True:

            option = self.pick_option(options)

            if option is not None:
                option[2]()

    def pick_option(self, options, key=lambda x:x[0], description=lambda x:x[1]):

        while True:
            try:
                for option in options:
                    print(f"{key(option)} - {description(option)}")

                line = ''

                key = input('\nOption> ').strip()

                if not key:
                    return None
                
                for option in options:
                    if option[0] == key:
                        return option
                else:
                    raise ValueError()
                
            except ValueError:
                print("Invalid option: " + line)

            except KeyboardInterrupt:
                sys.exit(0)

p = Program()
p.run()
