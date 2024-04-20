import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from requests import RequestException
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (
    BASE_DIR, DOWNLOADS_DIR, EXPECTED_STATUS, MAIN_DOC_URL, MAIN_PEP_URL
)
from exceptions import LatestVersionsMissingException, ParserFindTagException
from outputs import control_output
from utils import create_soup, find_tag, get_response


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    soup = create_soup(session, whats_new_url)

    sections_by_python = soup.select(
        '#what-s-new-in-python div.toctree-wrapper li.toctree-l1'
    )

    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = section.find('a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features='lxml')
        results.append(
            (
                version_link,
                find_tag(soup, 'h1').text,
                find_tag(soup, 'dl').text.replace('\n', ' ')
            )
        )

    return results


def latest_versions(session):
    soup = create_soup(session, MAIN_DOC_URL)

    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise LatestVersionsMissingException('Ничего не нашлось')

    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        text_match = re.search(pattern, a_tag.text)
        if text_match:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append((a_tag['href'], version, status))

    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    soup = create_soup(session, downloads_url)

    pdf_a4_link = soup.select_one(
        'div.body table.docutils a[href$="pdf-a4.zip"]'
    )['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)

    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / DOWNLOADS_DIR
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename

    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)

    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    soup = create_soup(session, MAIN_PEP_URL)
    if soup is None:
        return

    main_tag = find_tag(soup, 'section', {'id': 'numerical-index'})
    table_tag = find_tag(main_tag, 'tbody')
    row_tags = table_tag.find_all('tr')

    errors = []
    mismatch = []
    statuses = {}
    for row_tag in tqdm(row_tags):
        try:
            preview_status_tag = find_tag(row_tag, 'abbr')
            preview_status = EXPECTED_STATUS[preview_status_tag.text[1:]]
            a_tag = find_tag(row_tag, 'a', {'class': 'pep reference internal'})
            href = a_tag['href']
            link = urljoin(MAIN_PEP_URL, href)
            soup = create_soup(session, link)
            status_tag = find_tag(soup, 'abbr')
            page_status = status_tag.text
            statuses[page_status] = statuses.get(page_status, 0) + 1
            if page_status not in preview_status:
                mismatch.append((link, page_status, preview_status))
        except (ParserFindTagException, RequestException) as error:
            errors.append(error)

    for error in errors:
        logging.error(f'Ошибка: {error}')
    if mismatch:
        logging.info('Обнаружены несовпадающие статусы! \n')
        for pep in mismatch:
            logging.info(
                f'{pep[0]} \n'
                f'Статус в карточке: {pep[1]} \n'
                f'Ожидаемые статусы: {pep[2]} \n'
            )
    return [
        ('Статус', 'Количество'),
        *statuses.items(),
        ('Total', sum(statuses.values())),
    ]


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():
    try:
        configure_logging()
        logging.info('Парсер запущен!')

        arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
        args = arg_parser.parse_args()
        logging.info(f'Аргументы командной строки: {args}')

        session = requests_cache.CachedSession()
        if args.clear_cache:
            session.cache.clear()

        parser_mode = args.mode
        results = MODE_TO_FUNCTION[parser_mode](session)
        if results:
            control_output(results, args)
    except Exception as error:
        logging.error(f'Ошибка: {error}', stack_info=True)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
