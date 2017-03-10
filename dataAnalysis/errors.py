class DataExtractError(Exception):
    pass


class NoEventsError(DataExtractError):
    pass


class MissingMarkersError(DataExtractError):
    pass


class TooManyBadBitsError(DataExtractError):
    pass
