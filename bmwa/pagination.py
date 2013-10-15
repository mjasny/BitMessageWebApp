from flask import url_for, request

from .core import app


class Pagination:

    def __init__(self, page, items, per_page, nearby=3):
        self.page = page
        self.items = items
        self.per_page = per_page
        self.nearby = nearby

        self.item_count = len(items)
        self.page_count = 1 + self.item_count // per_page

        if page < 1 or page > self.page_count:
            raise IndexError("Page out of range.")

        self.start = (page - 1) * per_page
        self.stop = self.start + per_page
        self.stop = min(self.stop, self.item_count)

    def get_slice(self):
        return self.items[self.start: self.stop]

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.page_count

    def iter_nearby_pages(self, nearby=None):
        if nearby is None:
            nearby = self.nearby

        for i in range(self.page - nearby, self.page + nearby + 1):
            if i <= 1:
                continue
            elif i >= self.page_count:
                break

            yield i


def url_for_pagination(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)
app.jinja_env.globals['url_for_pagination'] = url_for_pagination
