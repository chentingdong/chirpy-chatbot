# TODO: to be deprecated in illusionist 3.0. Delete with engine.py.


# import re
# import json
# from python_utils.config import server_config
#  from python_utils.logger import logger_console
# 
# result_pattern = re.compile('!title!(.*)!summary!(.*)!highlight!(.*)!article_url!(.*)', re.DOTALL)
# 
# answer_schema = {
#     'type': 'object',
#     'properties': {
#         'title': {'type': 'string'},
#         'summary': {'type': 'string'},
#         'url': {'type': 'string'},
#         'date': {'type': 'string'}
#     }
# }
# 
# def markup(answer: str) -> str:
#     matches = result_pattern.match(answer)
#     title = '<p class="title">%s</p>' % matches.group(1)
#     url = '<p class="url">%s</p>' % matches.group(4)
#     words = matches.group(2).split(' ')
#     total_num_words = len(words)
#     highlights = matches.group(3).split(',')
#     num_highlights = len(highlights)
#     for i in range(num_highlights):
#         try:
#             b = int(highlights[i])
#             if b > config.num_words_ret or b > total_num_words:
#                 break
#             words[b] = '<p class="highlight">%s</p>' % words[b]
#         except:
#             pass
#     summary = ' '.join(words[:config.num_words_ret])
#     if total_num_words > config.num_words_ret:
#         summary += ' ...'
#     return '\n'.join([title, summary, url])
# 
# 
# def to_json(answer: str) -> str:
#     matches = result_pattern.match(answer)
#     if matches is not None:
#         title = matches.group(1)
#         words = matches.group(2).split(' ')
#         total_num_words = len(words)
#         highlights = matches.group(3).split(',')
#         num_highlights = len(highlights)
#         url = matches.group(4)
#         logger_console.debug('title: ' + title)
#         logger_console.debug('summary: ' + ' '.join(words))
#         logger_console.debug('url: ' + url)
#         logger_console.debug('highlights: ' + ' '.join(highlights))
#         # assuming highlights are in the ascending order
# 
#         for i in range(num_highlights):
#             try:
#                 b = int(highlights[i])
#                 if b > config.num_words_ret or b > total_num_words:
#                     break
#                 words[b] = '*%s*' % words[b]
#             except:
#                 pass
#         summary = ' '.join(words[:config.num_words_ret])
#         if total_num_words > config.num_words_ret:
#             summary += ' ...'
#         summary = re.sub(r"http:[ ]*(.)", r"http:\1", summary)
#         summary = re.sub(r"http:([^/])", r"http://\1", summary)
# 
#         return json.dumps({'title': title, 'summary': summary, 'url': url, 'date': ''})
#     else:
#         return json.dumps({'title': '', 'summary': '', 'url': '', 'date': ''})
# 
