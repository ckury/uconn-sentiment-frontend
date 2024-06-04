'''
datastore.py module for UCONN Sentiment Analysis

This module interfaces with GCP datastore to do the following:

queryEntities -> Fetches all entities in a given namespace and kind
createEntity -> Creates an entity
queryKinds -> Gets all kinds in a given namespace
queryIds -> Gets all entity ids in a given kind
checkEntity -> Checks to see if entity exists which matches data
updateEntity -> Changes the data of an existing entity
removeEntity -> Removes an existing entity

Note: GCP credentials need to be set as environmental variable when running the python program

author: Charlie Kuryluk
date: 6/3/2024

'''

from google.cloud import datastore

datastoreClient = datastore.Client()

def queryEntities(kind: str, namespace: str = None, order: str = None, filters: list | dict = None, limit: int = None, _ids_only: bool = False) -> list:
    ''' queryEntities() takes the following arguments:

        - kind: String containing kind (required)
        - namespace: String containing the namespace (optional)
        - order: String containing name of property to sort by (optional)
        - filters: List or dict containing tuples of arguments to be passed to query.add_filter() (optional)
        - limit: Integer with max number of entities to fetch (optional)

        Returns a list of entities which match the parameters.

        To parse the enitites, treat the entity as a dictionary (NOTE: Kind and ID of entity are stored as attributes)

        Usage example:

        results = queryEntities(kind='Example Kind', order='Property1', filters=[('Property2', '=', 3)])

        for entity in results:
            print(entity['Property1'] + entity['Property2'])    -> Property1Property2 \n
            print(entity.key.id)                                -> EntityID           \n
            print(entity.key.kind)                              -> 'Example Kind'     \n

    '''

    if namespace != None: 
        # Create query with provided namespace and kind
        query = datastoreClient.query(namespace=namespace, kind=kind)

    else:
        # Create query with provided kind and default namespace
        query = datastoreClient.query(kind=kind) 


    if order != None:
        # Modifies query to include order parameter if defined
        query.order = [order]

    if filters != None:
        # Adds filters to query
        for filter in filters:

            if type(filter) is tuple:
                query.add_filter(*filter)

            if type(filter) is dict:
                query.add_filter(**filter)

    if _ids_only != False:
        query.keys_only()

    # Returns all entities from query in list format
    return list(query.fetch(limit=limit))

def createEntity(kind: str, data: dict, namespace: str = None) -> str:
    ''' createEntity() takes the following arguments:

        - kind: String containing kind (required)
        - data: Dictionary containing property names as keys and values as values (required)
        - namespace: String containing the namespace (optional)
        
        Returns a string with the ID of the new entity.

        Usage example:

        id = createEntity(kind='Example Kind', data={ "property1": "value1" })

    '''
    entity = datastoreClient.entity(datastoreClient.key(kind, namespace=namespace))
    
    entity.update(data)

    try:
        datastoreClient.put(entity=entity)
        return entity.key.id

    except:
        return
    
def queryKinds(namespace: str = None) -> list:
    ''' queryKinds() takes the following argument:

        - namespace: String containing the namespace (required)

        Returns a list of kinds in provided namespace.

    '''
    query = datastoreClient.query(kind='__kind__', namespace=namespace)
    query.keys_only()

    output = []

    for entity in query.fetch():
        if not entity.key.id_or_name[0] == "_":
            # Removes internal only kinds
            output.append(entity.key.id_or_name)
            
    return output

def queryIds(*args, **kwargs):
    ''' queryIds() is a proxy function of queryEntities() and takes the same arguments.

        Returns a list of ids of entities which match the filters.

    '''

    result = queryEntities(*args, _ids_only=True, **kwargs)
    
    output = []

    for entity in result:
        output.append(entity.key.id)

    return output

def checkEntity(id:str, kind: str, namespace: str = None) -> datastore.Entity:
    ''' checkEntity() takes the following arguments:

        - kind: String containing kind (required)
        - namespace: String containing the namespace (optional)

        Returns entity if present and None if not present

    '''

    id = int(id)

    key = datastoreClient.key(kind, id, namespace=namespace)

    output = datastoreClient.get(key=key)

    return output

def updateEntity(entity: datastore.Entity, data:dict):
    ''' updateEntity() takes the following arguments:

        - entity: Datastore Entity from either checkEntity() or queryEntities()
        - data: Dictionary of keys (properties) and values to update

        Doesn't return a value.

        Usage Example:

        existing_entity = checkEntity(data, kind)

        updateEntity(existing_entity, {"Property1":"Value1"})

    '''

    for key, value in data.items():
        entity[key] = value

    datastoreClient.put(entity=entity)

    return

def removeEntity(entity: datastore.Entity):
    ''' removeEntity() takes the following argument:

        - entity: Datastore Entity from either checkEntity() or queryEntities()

        Doesn't return a value.

        Usage Example:

        existing_entity = checkEntity(data, kind)

        removeEntity(existing_entity)

    '''

    datastoreClient.delete(entity.key)

    return