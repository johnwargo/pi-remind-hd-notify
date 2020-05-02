# import datetime
from datetime import datetime

start_time = '08:30'
end_time = '17:45'

# the_time = datetime.time(start_time)
the_time = datetime.strptime(start_time, '%H:%M').time()
print(the_time)

the_time = datetime.strptime(end_time, '%H:%M').time()
print(the_time)