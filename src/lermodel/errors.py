class UnsupportedFeatureTypeError(ValueError):
    """
    Raised by a version package's to_lerfeat() when feature_type names a
    real LER feature type that this package hasn't implemented yet (see
    clay/adr/944) - as opposed to a plain ValueError for malformed/missing
    input.
    """
