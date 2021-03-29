# TODO: to be deprecated in illusionist 3.0. Need to follow response standard.

from illusionist.status import Status


class Response:
    def __init__(self):
        self.session_id = ""
        self.conversation_id = ""
        self.request_id = ""
        self.predict_request_id = ""
        self.luke_request_id = ""
        self.response = False
        self.reason = ""
        self.payloads = {}
        self.status = Status.HTTP_200_OK

    def add_payload(self, name, payload):
        self.payloads[name] = payload

    def failure(self, reason="Unknown", status=Status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.response = False
        self.reason = reason
        self.status = status

    def success(self, status=Status.HTTP_200_OK): # could be 201 or 204
        self.response = True
        self.status = status

    @property
    def object(self):
        obj = {"response": self.response}
        if not self.response:
            obj["reason"] = self.reason
        obj["status"] = self.status
        obj["payloads"] = self.payloads
        obj["session_id"] = self.session_id
        obj["request_id"] = self.request_id
        obj["predict_request_id"] = self.predict_request_id
        obj["luke_request_id"] = self.luke_request_id
        obj["conversation_id"] = self.conversation_id
        return obj
