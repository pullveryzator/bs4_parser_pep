import re
from urllib.parse import urljoin
import logging

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, MAIN_DOC_URL, PEP_PAGE, EXPECTED_STATUS
from exceptions import ParserFindTextException
from outputs import control_output
from utils import get_response, find_tag, find_all_tags


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = find_all_tags(
        div_with_ul, 'li', attrs={'class': 'toctree-l1'}
    )
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]
    for section in tqdm(sections_by_python, colour='BLUE'):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features='lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append((version_link, h1.text, dl_text))
    return results


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    sidebar = find_tag(soup, 'div', {'class': 'sphinxsidebarwrapper'})
    ul_tags = find_all_tags(sidebar, 'ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = find_all_tags(ul, 'a')
            break
    else:
        raise ParserFindTextException(
            f'Строка "All versions" в теге {ul} не найдена.'
        )
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        href = a_tag['href']
        link = urljoin(MAIN_DOC_URL, href)
        if re.fullmatch(pattern=pattern, string=a_tag.text):
            version = re.search(
                string=a_tag.text, pattern=pattern
            ).group('version')
            status = re.search(
                string=a_tag.text, pattern=pattern
            ).group('status')
        else:
            version = a_tag.text
            status = ''
        results.append((link, version, status))
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    div_tag = find_tag(soup, 'div', {'role': 'main'})
    table_tag = find_tag(div_tag, 'table', {'class': 'docutils'})
    pdf_a4_tag = find_tag(
        table_tag,
        'a', {'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    pdf_a4_link = pdf_a4_tag['href']
    archive_link = urljoin(downloads_url, pdf_a4_link)
    filename = archive_link.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = get_response(session, archive_link)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    results = [('Статус', 'Количество')]
    temp_list = []
    unexpected_status = {}
    response = get_response(session, PEP_PAGE)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    tbody_tag = find_tag(
        find_tag(soup, 'section', {'id': 'numerical-index'}), 'tbody'
    )
    tr_tags = find_all_tags(tbody_tag, 'tr')
    for tr_tag in tqdm(tr_tags):
        a_tag = find_tag(tr_tag, 'a')
        pep_link = a_tag['href']
        abbr_tag = find_tag(tr_tag, 'abbr')
        status_out = abbr_tag.text[1:]
        pep_full_link = urljoin(PEP_PAGE, pep_link)
        pep_response = get_response(session, pep_full_link)
        pep_soup = BeautifulSoup(pep_response.text, features='lxml')
        dl_tag = find_tag(
            find_tag(pep_soup, 'section', {'id': 'pep-content'}), 'dl'
        )
        status_in = next(
            (dt_tag.find_next_sibling().string for dt_tag in
             find_all_tags(dl_tag, 'dt')
                if dt_tag.text == 'Status:'), None)
        if status_in:
            if status_in in EXPECTED_STATUS[status_out]:
                temp_list.append(status_out)
            else:
                expected_status = ', '.join(EXPECTED_STATUS[status_out])
                logging.info(
                    f'\nНесовпадающие статусы:\n{pep_full_link}\n'
                    f'Статус в карточке: {status_in}\n'
                    f'Ожидаемые статусы: {expected_status}')
                temp_list.append(status_in)
                unexpected_status[status_in] = (status_in, )
    EXPECTED_STATUS.update(unexpected_status)
    results.extend(
        (', '.join(EXPECTED_STATUS[key]), temp_list.count(key)) for key in
        EXPECTED_STATUS)
    results.append(('Total', len(temp_list)))
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():
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
    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
