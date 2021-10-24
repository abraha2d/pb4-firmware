from views import connect, index, scan

urlconf = {
    "/": index,
    "/connect": connect,
    "/scan": scan,
}
