from python_utils.solr import Solr


def test_create_solr_collection():
    solr = Solr()
    collection_name = "test_solr"
    solr.create_solr_collection(collection_name=collection_name)


def test_update_solr_collection():
    solr = Solr()
    collection_name = 'test_solr'
    docs = [
        {"id": "test_document_id", "title_t": "title_test1", "annotate_description_ent": "annotate_escription_test1"},
        {"id": "test_document_id2", "title_t": "title_test2", "annotate_description_ent": "annotate_escription_test2"}
    ]
    solr.update_solr_collection(collection_name=collection_name, docs=docs)


def test_search_solr_collection():
    solr = Solr()
    collection_name = "test_solr"
    query = "id:test_document_id"
    result = solr.search_solr_collection(collection_name=collection_name, query=query)
    assert len(result) == 1
    assert result[0]['annotate_description'] == 'annotate_escription_test1'


if __name__ == '__main__':
    test_create_solr_collection()
    test_update_solr_collection()
    test_search_solr_collection()
