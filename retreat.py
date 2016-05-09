import re

import httplib2
from bs4 import BeautifulSoup
import bs4

from slack import Slack

http = httplib2.Http()


def fetch() -> str:
    response, content = http.request('https://biwako-booking.doshisha.ac.jp/ajaxs/calendar?ym=201509')

    if response['status'] != '200':
        raise Exception(response['status'])

    return content.decode('UTF-8')


def calc(day: list) -> int:
    limit = [6, 1, 2, 10, 4]
    count = 0

    for i in range(5):
        count += day[i] * limit[i]

    '''
    和室: 6
    洋室（シングル）: 1
    洋室（ツイン）: 2
    キャビン（山小屋風の一戸建て）　1～3: 10
    キャビン　4～5: 4
    '''

    return count


def parse(html: str) -> list:
    return list(
        map(
            lambda day: calc(list(day)),
            map(
                lambda x: map(
                    lambda row: int(re.sub('(\(|\))', '', row.get_text())),
                    filter(
                        lambda tags: type(tags) == bs4.Tag,
                        list(x.children)[1:]
                    )
                ),
                BeautifulSoup(html).find_all('li', class_='yoyaku-ok')
            )
        )
    )


def mask(vacancy: list) -> list:
    for i in range(25, 30):
        vacancy[i] = 0

    return vacancy


def search(vacancy: list) -> list:
    choices = []

    i = 0

    while True:
        if i >= len(vacancy) - 2:
            break

        if vacancy[i] >= 30 and vacancy[i + 1] >= 30:
            choices.append(
                '9月{:d}日 (最大{:d}人) 〜 9月{:d}日 (最大{:d}人) 〜 9月{:d}日'.format(
                    i + 1, vacancy[i], i + 2, vacancy[i + 1], i + 3
                )
            )

        i += 1

    return choices


def notice(candidates: list):
    if len(candidates):
        Slack.notice(
            'TYPE YOUR ENDPOINT',
            'わんちゃんありやなぁ・・・\n' + '\n'.join(candidates) + '\n今すぐ予約! → https://biwako-booking.doshisha.ac.jp/'
        )


def main():
    notice(search(mask(parse(fetch()))))


if __name__ == "__main__":
    main()
