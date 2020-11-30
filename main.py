from ClientSocket import ClientSocket


def OnClientConnect(LogMessage):
    print(LogMessage)


def OnClientReconnect(LogMessage):
    print(LogMessage)


def OnClientSend(LogMessage, Content):
    print(LogMessage)


def OnClientReceive(LogMessage, Content):
    # MessageCode = int.from_bytes(self.__Message[0:2], byteorder="little")
    print(LogMessage)


def OnClientDisconnect(LogMessage):
    print(LogMessage)


def OnClientWarning(LogMessage):
    print(LogMessage)


def OnClientException(LogMessage):
    print(LogMessage)


if __name__ == '__main__':
    # Initialize our client settings
    ClientSock = ClientSocket("127.0.0.1", 1669)
    ClientSock.SetHeaderSize(4)  # 4 Bytes
    ClientSock.SetMaximumMessageSize(1024 * 1024)  # 1 MB
    # Register the call back handlers
    ClientSock.RegisterCallback(ClientSock.OnClientConnectEvent, OnClientConnect)
    ClientSock.RegisterCallback(ClientSock.OnClientReconnectEvent, OnClientReconnect)
    ClientSock.RegisterCallback(ClientSock.OnClientSendEvent, OnClientSend)
    ClientSock.RegisterCallback(ClientSock.OnClientReceiveEvent, OnClientReceive)
    ClientSock.RegisterCallback(ClientSock.OnClientDisconnectEvent, OnClientDisconnect)
    ClientSock.RegisterCallback(ClientSock.OnClientWarningEvent, OnClientWarning)
    ClientSock.RegisterCallback(ClientSock.OnClientExceptionEvent, OnClientException)
    # Connect to the server
    ClientSock.Connect()
