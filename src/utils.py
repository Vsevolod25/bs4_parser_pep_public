from requests import RequestException

from exceptions import ParserFindTagException


def get_response(session, url):
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response
    except RequestException as error:
        raise error(
            f'Возникла ошибка при загрузке страницы {url}',
        )


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        raise ParserFindTagException(f'Не найден тег {tag} {attrs}')
    return searched_tag
