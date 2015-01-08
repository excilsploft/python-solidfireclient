from solidfireclient import sfapi


class Cluster(sfapi.API):
    def GetClusterVersionInfo(self):
        params = None
        response = self.issue_api_request('GetClusterVersionInfo',
                                          params,
                                          endpoint_dict=None)
        return response
