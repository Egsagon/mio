'''
API wrapper for temp-mail.io
'''

from __future__ import annotations

import re
import time
import requests
from typing import Callable
from datetime import datetime
from dataclasses import dataclass

API = 'https://api.internal.temp-mail.io/api/v3/email/'
API_AT = 'https://api.internal.temp-mail.io/api/v3/attachment/'

@dataclass
class Mailer:
    '''
    Represent a mail sender or receiver.
    '''

    name: str = None
    address: str = None

@dataclass
class File:
    '''
    Represents a mail attachment.
    '''
    
    mail: MIO = None
    
    id: str = None
    url: str = None
    name: str = None
    size: int = None
    
    def download(self, path: str) -> None:
        '''
        Download the file to a destination.
        '''
        
        with open(path, 'wb') as file:
            res = self.mail.session.get(self.url)
            res.raise_for_status()
            
            file.write(res.content)

@dataclass
class Message:
    '''
    Represents a mail message.
    '''

    # Headers
    id: str = None
    author: Mailer = None
    cc: list[Mailer] = None
    subject: str = None
    date: datetime = None
    
    # Body
    body: str = None
    html: str = None
    files: list[File] = None

class MIO:
    '''
    Represents a temorary mail address.
    '''
    
    def __init__(self, address: str = None) -> None:
        '''
        Initialise a new mail instance.
        '''
        
        self.session = requests.Session()
        
        if address:
            data = { 'email': address }
        
        else:    
            # Get new address
            response = self.session.post(API + 'new', {'min_name_length': 10,
                                                    'max_name_length': 10})
            
            response.raise_for_status()
            data = response.json()
            
        # Save data
        self.address = data['email']
        self.domain = self.address.split('@')[1]
    
    def __repr__(self) -> str:
        
        return self.address
    
    @property
    def messages(self) -> list[Message]:
        '''
        List of received messages.
        '''

        response = self.session.get(API + f'{self.address}/messages')
        response.raise_for_status()
        
        return [Message(id = data['id'],
                        author = Mailer(re.findall(r'\"(.*?)\" <(.*?)>', data['from'])[0]),
                        cc = 'TODO',
                        subject = data['subject'],
                        date = data['created_at'], # TODO
                        body = data['body_text'],
                        html = data['body_html'],
                        files = [File(mail = self,
                                      id = file['id'],
                                      url = API_AT + file['id'],
                                      name = file['name'],
                                      size = file['size'])
                                 for file in data['attachments']])
                for data in response.json()]

    def wait(self,
             filter: Callable[[Message], bool] = None,
             max_time: int = 0,
             check_time: int = 5) -> Message:
        '''
        Wait for a message to be received.
        '''
        
        start = time.perf_counter()
        
        while 1:
            for message in self.messages:
                if filter is None or filter(message):
                    return message
            
            if max_time and time.perf_counter() - start > max_time:
                raise TimeoutError('Reached timeout before message reception')
            
            time.sleep(check_time)
    
    def delete(self) -> None:
        '''
        Delete the email address.
        '''

        response = self.session.delete(API + self.address)
        response.raise_for_status()

def new() -> MIO:
    '''
    Generate a new email address.
    '''
    
    return MIO()

def get(address: str) -> MIO:
    '''
    Recover an already created address.
    '''
    
    return MIO(address)

__all__ = [ 'new', 'get' ]

# EOF