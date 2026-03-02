import os
import logging
from azure.monitor.opentelemetry import configure_azure_monitor

logger = logging.getLogger('brand-gaurdian-telemetry')

def setup_telemetry():
    '''
    Initializes Azure Monitor OpenTelemetry
    Tracks: HTTP requests , database queries, errors, performance metrics 
    Sends this data to azure monitor
    it auto captures every API request
    No need to manually log each endpoint
    '''

    connection_string = os.getenv('APPLICATIONINSIGHTS_CONNECTION_STRING')

    if not connection_string:
        logger.warning('No instrumentation key found. Telemetry is Disabled')
        return
    
    # configure the azure monitor

    try:
        configure_azure_monitor(
            connection_string = connection_string,
            logger_name = 'brand-project-tracer',
        )
        logger.info('Azure Monitor Tracking Enabled and Connected')
    except Exception as e:
        logger.error(f'Failed to initialized Azure Monitor : {e}')