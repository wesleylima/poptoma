# poptoma

A Python API for interacting with Optoma projectors through web interface

## Sample Usage
```
from poptoma import Projector

projector = Projector('192.168.1.420', 'admin', 'admin')
projector.power_status() # false


projector.turn_on()
projector.power_status() # true

projector.turn_off()
projector.power_status() # false

```

The default password is `admin`. PLEASE change this
