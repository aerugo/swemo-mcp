"""
OpenAPI specifications for the Riksbank APIs.
"""

# Monetary Policy API OpenAPI Specification
MONETARY_POLICY_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "Riksbank Monetary Policy API",
        "description": "API for accessing Riksbank monetary policy data",
        "version": "1.0.0"
    },
    "servers": [
        {
            "url": "https://api.riksbank.se/monetary-policy/v1",
            "description": "Production server"
        }
    ],
    "paths": {
        "/forecasts": {
            "get": {
                "summary": "Get forecast data",
                "description": "Retrieve forecast data for a specific series",
                "parameters": [
                    {
                        "name": "series",
                        "in": "query",
                        "description": "Series identifier",
                        "required": True,
                        "schema": {
                            "type": "string"
                        }
                    },
                    {
                        "name": "policy_round_name",
                        "in": "query",
                        "description": "Policy round identifier",
                        "required": False,
                        "schema": {
                            "type": "string"
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "data": {
                                            "type": "array",
                                            "items": {
                                                "type": "object"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/forecasts/policy_rounds": {
            "get": {
                "summary": "List policy rounds",
                "description": "Retrieve a list of all available policy rounds",
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "data": {
                                            "type": "array",
                                            "items": {
                                                "type": "object"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/forecasts/series_ids": {
            "get": {
                "summary": "List series IDs",
                "description": "Retrieve a list of all available series IDs",
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "data": {
                                            "type": "array",
                                            "items": {
                                                "type": "object"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

# SWEA API OpenAPI Specification
SWEA_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "Riksbank SWEA API",
        "description": "API for accessing Riksbank SWEA data",
        "version": "1.0.0"
    },
    "servers": [
        {
            "url": "https://api.riksbank.se/swea/v1",
            "description": "Production server"
        }
    ]
}

# SWESTR API OpenAPI Specification
SWESTR_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "Riksbank SWESTR API",
        "description": "API for accessing Riksbank SWESTR data",
        "version": "1.0.0"
    },
    "servers": [
        {
            "url": "https://swestr.riksbank.se/api/v1",
            "description": "Production server"
        }
    ]
}
