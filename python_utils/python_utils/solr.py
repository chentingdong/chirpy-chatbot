import traceback
import requests
from python_utils.logger import logger_console
from python_utils.config import server_config


class Solr:

    def __init__(self):
        self.url_prefix = '{host}:{port}/solr'.format(host=server_config['solr']['host'],
                                                      port=server_config['solr']['port'])

    def create_solr_collection(self, collection_name, num_shards=1, replication_factor=2, max_shards_per_node=3,
                               config_source=None):
        """
        Create a collection in Solr
        :param collection_name: the name of the collection
        :type collection_name: str
        :param num_shards: the number of shards, defaults to 1
        :type num_shards: int
        :param replication_factor: the number of replications, defaults to 2
        :type replication_factor: int
        :param max_shards_per_node: the maximum number of shards to be stored in a node, defaults to 3
        :type max_shards_per_node: int
        :param config_source: the name of the config folder
        :type  config_source: str
        :return: True if succeeds or already exists
        :rtype: bool
        """
        solr_url = '{url_prefix}/admin/collections'.format(url_prefix=self.url_prefix)
        if not config_source:
            config_source = server_config.get('SOLR_CONFIG_NAME', 'neva')
        try:
            res = requests.get(solr_url, params={'action': 'CREATE', 'name': collection_name, 'numShards': num_shards,
                                                 'replicationFactor': replication_factor,
                                                 'maxShardsPerNode': max_shards_per_node,
                                                 'collection.configName': config_source})
            return res.status_code == 200 or \
                   (res.status_code == 400 and res.content.decode('utf-8').find('collection already exists') >= 0)
        except:
            msg = 'Can not create collection {}'.format(collection_name)
            logger_console.warning(msg)
            logger_console.error(traceback.format_exc())
            return False

    def reload_collection(self, collection_name):
        """
        When Solr is run in standalone mode, we need to reload the core(collection) after updating.
        """
        solr_url = "{url_prefix}/admin/cores?action=RELOAD&core={collection_name}".format(
            url_prefix=self.url_prefix, collection_name=collection_name)
        try:
            res = requests.get(solr_url)
            return res.status_code == 200
        except:
            msg = "Cannot reload core(collection) {}".format(collection_name)
            logger_console.warning(msg)
            logger_console.error(traceback.format_exc())
            return False

    def update_solr_collection(self, collection_name, docs, chunk_size=1000):
        """
        Update a collection in Solr with given documents, if they don't exist, the documents will be added
        :param collection_name: the name of the collection
        :type collection_name: str
        :param docs: the list of documents to update
        :type docs: List[Dict]
        :return: a list of response header
        :rtype: List
        """
        start = 0
        docs_all = docs
        while start < len(docs_all):
            docs = docs_all[start: start + chunk_size]
            if not all((isinstance(doc, dict) and 'id' in doc for doc in docs)):
                msg = 'Can not update the documents, some of them are not formatted well {}'.format(docs)
                logger_console.warning(msg)
                logger_console.debug(traceback.format_exc())
                return []

            solr_url = '{url_prefix}/{collection_name}/update?'.format(url_prefix=self.url_prefix,
                                                                       collection_name=collection_name)
            try:
                res = requests.post(solr_url, json=docs)
                logger_console.debug(res.json())
                start += chunk_size
            except:
                msg = 'Can not update documents {} in {} '.format(docs, collection_name)
                logger_console.warning(msg)
                logger_console.debug(traceback.format_exc())
                return []
        return res.status_code == 200

    def delete_docs_from_collection(self, collection_name, condition):
        """
        Delete documents from a collection in Solr with given condition
        :param collection_name: the name of the collection
        :type collection_name: str
        :param condition: query to delete documents. eg. id:id AND doc_number_t:doc
        :type condition: str
        :return: True if succeeds
        :rtype: bool
        """
        solr_url = """{url_prefix}/{collection_name}/update? """.format(
            url_prefix=self.url_prefix, collection_name=collection_name)
        delete_docs = {"delete": {"query": condition}}
        try:
            res = requests.post(solr_url, json=delete_docs)
            logger_console.debug(res.json())
            return res.status_code == 200
        except:
            msg = 'Can not delete documents from {}'.format(collection_name)
            logger_console.warning(msg)
            logger_console.debug(traceback.format_exc())
            return False

    @staticmethod
    def remove_suffix(doc):
        """
        Remove the suffix in suffixes list from the end of each field name.
        :param doc: the Solr search result
        :type doc: dict
        :return: Solr search result with suffix removed from the field names.
        :rtype: dict
        """
        suffixes = ["_t", "_en", "_ent", "_st"]
        res = dict()
        for field in doc:
            key = field
            for suffix in suffixes:
                if field.endswith(suffix):
                    field = field[:-len(suffix)]
                    break  # Since we only added the suffix once, we don't want to trim more than once.
            res[field] = doc[key]
        return res

    def search_solr_collection_dismax(self, collection_name, query, rows=100, weights=''):
        """
        Search a collection in Solr
        :param weights: weight of each column
        :type weights: str
        :param collection_name: the name of the collection
        :type collection_name: str
        :param query: the query string
        :type query: str
        :param rows: the number of rows to return
        :type rows: int
        :return: a list of documents retrieved from Solr
        :rtype: List
        """
        solr_url = """{url_prefix}/{collection_name}/select""".format(
            url_prefix=self.url_prefix, collection_name=collection_name)
        try:
            logger_console.debug('solr_url: {}'.format(solr_url))
            params = {'q': query, 'defType': 'dismax', 'qf': weights, 'fl': '*, score', 'rows': rows, 'wt': 'json'}
            logger_console.debug('solr_params: {}'.format(params))
            res = requests.get(solr_url, params=params)
            result = [self.remove_suffix(doc) for doc in res.json()['response']['docs']]
            logger_console.debug('solr response docs length: {}'.format(len(result)))
            return result
        except:
            msg = 'Can not retrieve documents from {} for query {}'.format(collection_name, query)
            logger_console.warning(msg)
            logger_console.debug(traceback.format_exc())
            return []

    def search_solr_collection(self, collection_name, query, rows=100, sort=None, start=0, fl='*, score',
                               fq=None, debug=None, explain_other=None, time_allowed=-1, omit_header=None):
        """
        Search a collection in Solr. All common query parameters supported by Solr 4.10 are supported here except
        for those who need special handling, i.e., defType, wt, logParamsList.
        :param collection_name: the name of the collection
        :type collection_name: str
        :param query: the query string
        :type query: str
        :param rows: the number of rows to return
        :type rows: int
        :param sort: Sorts the response to a query in either ascending or descending order.
        :type sort: str
        :param start: the index of the first result to be returned.
        :type start: int
        :param fl: the list of the fields to be returned.
        :type fl: str
        :param debug: request additional debugging information in the response.
        :type debug: str
        :param fq: the filter query to send to Solr
        :type fq: str
        :param explain_other: Allows clients to specify a Lucene query to identify a set of documents.
        :type explain_other: str
        :param time_allowed: Defines the time allowed for the query to be processed.
        :type time_allowed: int
        :param omit_header: Excludes the header from the returned results, if set to true.
        :type omit_header: boolean
        :return: a list of documents retrieved from Solr
        :rtype: List
        """
        solr_url = '{url_prefix}/{collection_name}/select'.format(
            url_prefix=self.url_prefix, collection_name=collection_name)
        try:
            logger_console.debug('solr_url: {}'.format(solr_url))
            params = {'q': query, 'fl': fl, 'rows': rows, 'wt': 'json'}
            # Add optional parameters to the search parameters
            if fq:
                params['fq'] = fq
            if sort:
                params['sort'] = sort
            if start != 0:
                params['start'] = start
            if debug:
                params['debug'] = debug
            if explain_other:
                params['explainOther'] = explain_other
            if time_allowed != -1:
                params['timeAllowed'] = time_allowed
            if omit_header:
                params['omitHeader'] = omit_header
            logger_console.debug('solr_query: {}'.format(query))
            logger_console.debug('solr_params: {}'.format(params))
            res = requests.get(solr_url, params=params)
            result = [self.remove_suffix(doc) for doc in res.json()['response']['docs']]
            logger_console.debug('solr response docs length: {}'.format(len(result)))
            return result
        except:
            msg = 'Can not retrieve documents from {} for query {}'.format(collection_name, query)
            logger_console.warning(msg)
            logger_console.debug(traceback.format_exc())
            return []
