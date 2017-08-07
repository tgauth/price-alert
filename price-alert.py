#!/usr/bin/env python

import os
import re
import json
import time
import requests
import argparse
import urlparse
from copy import copy
from lxml import html


def get_price(url, selector):
    r = requests.get(url, headers={
        'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'
    })
    r.raise_for_status()
    tree = html.fromstring(r.text)
    try:
        # extract the price from the string
        price_string = re.findall('\d+.\d+', tree.xpath(selector)[0].text)[0]
        print(price_string)
        return float(price_string.replace(',', '.'))
    except IndexError, TypeError:
        print('Didn\'t find the \'price\' element, trying again later...')


def get_config(config):
    with open(config, 'r') as f:
        return json.loads(f.read())


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config',
                        default='%s/config.json' % os.path.dirname(
                            os.path.realpath(__file__)),
                        help='Configuration file path')
    parser.add_argument('-t', '--poll-interval', type=int, default=30,
                        help='Time in seconds between checks')
    return parser.parse_args()


def main():
    args = parse_args()
    config = get_config(args.config)
    items = config['items']

    while True and len(items):
        for item in copy(items):
            print('Checking price for %s (should be lower than %s)' % (
                item[0], item[1]))
            item_page = urlparse.urljoin(config['base_url'], item[0])
            price = get_price(item_page, config['xpath_selector'])
            if not price:
                continue
            elif price <= item[1]:
                print('Price is %s!! Go get it at: %s' % (price, item_page))
                items.remove(item)
            else:
                print('Price is %s. Ignoring...' % price)

        break

if __name__ == '__main__':
    main()
