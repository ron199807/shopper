from drf_spectacular.utils import OpenApiExample, OpenApiResponse
from drf_spectacular.types import OpenApiTypes

DASHBOARD_RESPONSE_EXAMPLE = {
    'stats': {
        'active_bids': 3,
        'won_bids': 5,
        'completed_bids': 2,
        'total_earnings': 450.50,
        'average_rating': 4.8,
        'completed_jobs': 7
    },
    'recent_bids': [
        {
            'id': 1,
            'amount': '235.00',
            'status': 'active',
            'shopping_list_title': 'Weekend Party Supplies',
            'created_at': '2026-02-20T14:30:00Z'
        }
    ],
    'nearby_lists': [
        {
            'id': 1,
            'title': 'Weekend Party Supplies',
            'store_city': 'New York',
            'estimated_total': '250.00',
            'bidding_deadline': '2026-02-25T18:00:00Z',
            'total_bids': 2
        }
    ]
}

WITHDRAW_BID_RESPONSE_EXAMPLE = {
    'message': 'Bid withdrawn successfully'
}