print("===IMPORTING urlconf.py===")
from views import connect, index

urlconf = {
    "/": index,
    "/connect": connect,
}
