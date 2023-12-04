## MIO - API wrapper for temp-mail.io

Use temp email address in you scripts easily.

### Quick start

#### Create new addresses
```python
>>> import mio

# Create a new mail
>>> mail = mio.new()
token@domain.ext

# List messages
>>> mail.messages
[Message(...), Message(...), ...]

# Get and download attachments
>>> mail[0].files[0].download('file.txt')
```

#### Recover old adresses
```python
>>> import mio

>>> mail = mio.get('token@domain.ext')
token@domain.ext

# Listen for messages that have 'work' in their subjects
>>> mail.wait( lambda msg: 'work' in msg.subject )
Message(...)

# Delete adress when done
>>> mail.delete()
```

### License

This project is licensed under the GPL-v3 license. See the `LICENSE` file.