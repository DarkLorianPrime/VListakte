def get_query_dict(query: bytes):
    query_dict = {query.split("=")[0]: query.split("=")[1]
                  for query in query.decode().split("&")
                  if len(query) > 0}
    return query_dict
