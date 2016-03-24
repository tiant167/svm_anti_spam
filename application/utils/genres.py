#!/usr/bin/env python
# coding: utf-8
'''
common http response json struct
'''

from datetime import datetime, timezone

def success_response(resp, status_code=200):
    '''
    sends success response to client
    '''
    payload = {
        'ok': True,
        'status': status_code,
        'now': datetime.now(timezone.utc).isoformat(),
        'data': resp
    }
    return payload, status_code

def fail_response(resp, status_code=400):
    '''
    sends fail response to client
    '''
    payload = {
        'ok': False,
        'status': status_code,
        'now': datetime.now(timezone.utc).isoformat(),
        'data': resp
    }
    return payload, status_code
