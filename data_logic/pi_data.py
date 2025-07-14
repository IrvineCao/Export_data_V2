query_params = {
    "count": """

    """,
    "data": """

    """
}

def get_query(query_name, storefront_placeholders, tag_placeholders):
    """
    Get a query by name and format it with storefront and tag placeholders
    
    Args:
        query_name (str): Name of the query to retrieve ('count' or 'data')
        storefront_placeholders (str): Placeholder string for storefront IDs (e.g., '%s, %s')
        tag_placeholders (str): Placeholder string for tags (e.g., '%s, %s')
        
    Returns:
        str: Formatted SQL query
    """
    return query_params[query_name].format(
        storefront_placeholders=storefront_placeholders,
        tag_placeholders=tag_placeholders
    )
