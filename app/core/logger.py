import logging

    # A logger needs a handler to decide where its messages should go.
    #   Logger
    #     ↓
    #   Handler (streanHandler)
    #     ↓
    #   formatter
    #     ↓
    #   Terminal
    

def get_logger(name:str):   #let name be "training" or "ingest" or "rag"
    logger = logging.getLogger(name)   #creates/retrieves a logger called training.



    if not logger.handlers:
        handler = logging.StreamHandler()    # A handler determines where the log message goes.
                                             # StreamHandler() normally sends the logs to the console/terminal.



    # create the log format
    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
        # 2026-09-04 02:30:15,123 | INFO | training | Model training started
    )


    handler.setFormatter(formatter)   # attach the formatter to the handler
    logger.addHandler(handler)        # attach the handler to the logger



    logger.setLevel(logging.INFO)     # set the logging level to INFO (you can change it to DEBUG, WARNING, etc.)
    # we get INFO & WARNING & RROR & CRITICAL

    return logger