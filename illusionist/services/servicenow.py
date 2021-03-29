from urllib import parse
from illusionist.models.service import Service
from python_utils.config import server_config

service_name = 'servicenow'


class ServiceNowForm(Service):
    def __init__(self, context):
        self.context = context
        agent_id = context.get_local('agent_id')
        super().__init__(agent_id=agent_id)
        self.params = self.get_params(agent_id, service_name)

    def build_links(self, data):
        """
        Sample response from luke
        {
            "code": "form",
            "data": {
            "info": [
                {
                    "component_id": 3,
                    "score": 0.7296252458123895,
                    "document_id": "011c15d4e9fd73cecdaf66140621f514",
                    "collection_id": "adidas_hr_kb_knowledge",
                    "title": "Who is eligible for the Group Accident Insurance?",
                    "display_info": {
                        "ext_doc_id": "9f6289dedb1d0704d3eff3361d961947"
                    },
                    "doc_type": "kb_knowledge",
                    "preview_data": [
                        "The Group Accident Insurance covers different levels of employee groups. The insurance sums are connected to
                        the GSMS Compensation & Benefits Structure (as part of the employment contract) or certain groups of employees (not mentioned in the employment contract)",
                        "Group Accident Insurance"
                    ]
                }
            ],
            "utterance": "Here is a list of HR documents that are most relevant to your request:",
            "domain": "HR"
            },
            "release_version": "3.5.0"
        }

        preview_data would be a list of values retrieved based on configuration done for search component in luke
        """
        domain = data.get('domain', 'it').upper()
        form_view_url_pattern = self.params.get('form_view_url_pattern').get(domain)
        forms = data.get('info', [])
        link_buttons = []
        instance_name = self.context.get_local('instance_name', self.params.get('instance_name'))
        for form in forms:
            form_url = form_view_url_pattern.format(
                    instance_name=instance_name,
                    document_id=form.get('display_info', {}).get('ext_doc_id')
                )

            host = server_config.get('events', {}).get('host')
            protocol = server_config.get('events', {}).get('protocol')
            url = '{protocol}://{host}/events' \
                  '?redirect_url={redirect_url}' \
                  '&app_id={app_id}' \
                  '&agent_id={agent_id}' \
                  '&source_request_id={request_id}' \
                  '&event_type={type}' \
                  '&event_value={document_id}'\
                .format(
                    protocol=protocol,
                    host=host,
                    redirect_url=parse.quote(form_url),
                    request_id=self.context.get_local('request_id'),
                    app_id=self.context.get_local('app_id', None),
                    agent_id=self.context.get_local('agent_id'),
                    type='click',
                    document_id=form.get('display_info', {}).get('ext_doc_id')
                )

            link_buttons.append({
                'title': form['title'],
                'url': url,
                'document_id': form['document_id'],
                'score': form['score'],
                'doc_type': form['doc_type'],
                'preview_data': form['preview_data']
            })
        return link_buttons

