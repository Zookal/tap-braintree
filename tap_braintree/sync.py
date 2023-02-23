import singer
from tap_braintree.streams import STREAMS

LOGGER = singer.get_logger()

# Currently syncing sets the stream currently being delivered in the state.
# If the integration is interrupted, this state property is used to identify
#  the starting point to continue from.
# Reference: https://github.com/singer-io/singer-python/blob/master/singer/bookmarks.py#L41-L46
def update_currently_syncing(state, stream_name):
    """
    Update currently_syncing value in state for given stream
    """

    if (stream_name is None) and ('currently_syncing' in state):
        del state['currently_syncing']
    else:
        singer.set_currently_syncing(state, stream_name)
    singer.write_state(state)

def get_selected_streams(catalog, state):
    """
    Return list of all selected fields from catalog
    """

    # Return list of all the selected streams in catalog
    selected_streams = []
    for stream in catalog.get_selected_streams(state):
        selected_streams.append(stream.stream)
    LOGGER.info('selected_streams: {}'.format(selected_streams))
    return selected_streams


def sync(gateway, config, catalog, state):
    """
    Run sync function for all the selected stream
    """

    LOGGER.info("Starting Sync")
    
    selected_streams = get_selected_streams(catalog, state)
    if not selected_streams or selected_streams == []:
        return
    
    # Get the streams to sync (based on dependencies)
    sync_streams = []
    
    # Loop thru all streams
    for stream_name, stream_class in STREAMS.items():
        # LOGGER.info('START Syncing: %s', stream_name)
        if stream_name in selected_streams:
            
            # If stream has a parent_stream, then it is a child stream
            parent_stream = stream_class.parent_stream
            
            LOGGER.info('stream: {}, parent: {}'.format(stream_name, parent_stream))
            
            if stream_name not in sync_streams:
                sync_streams.append(stream_name)
                
            if parent_stream and parent_stream not in sync_streams:
                sync_streams.append(parent_stream)
            
    LOGGER.info('Sync Streams: {}'.format(sync_streams))
    
    # Loop through selected_streams
    for stream_name in STREAMS:
        if stream_name not in sync_streams or STREAMS[stream_name].parent_stream != None:
            LOGGER.info("{}: Skipping - not selected".format(stream_name))
            continue
        
        stream = catalog.get_stream(stream_name)
        schema = stream.schema.to_dict()
        stream_obj = STREAMS[stream_name]()
        LOGGER.info('START Syncing: {}'.format(stream_name))
        stream_obj.write_schema(schema, stream_name, sync_streams, selected_streams)
        update_currently_syncing(state, stream_name)
        
        total_records = stream_obj.sync(
            gateway = gateway,
            config = config,
            schema = schema,
            state = state,
            selected_streams = selected_streams
        )
        
        update_currently_syncing(state, None)
        LOGGER.info('FINISHED Syncing: {}, total_records: {}'.format(stream_name, total_records))
    
    update_currently_syncing(state, None)
    LOGGER.info("Finished sync")
