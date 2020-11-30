from threading import Thread
from ClientSocket import ClientSocket


class Child:
    __COMMAND_NAME_GET_HANDSHAKE = "GetHandShake"  # 1
    __COMMAND_NAME_SET_HANDSHAKE = "SetHandShake"  # 2
    __COMMAND_NAME_GET_DETECTED_FRAME = "GetDetectedFrame"  # 3
    __COMMAND_NAME_SET_DETECTED_FRAME = "SetDetectedFrame"  # 4
    __COMMAND_NAME_TERMINATE = "Terminate"  # 5
    __COMMAND_NAME_ERROR = "Error"  # 6
    __COMMAND_NAME_INFO = "Information"  # 7
    __COMMAND_NAME_GET_STATUS = "GetChildStatus"  # 8
    __COMMAND_NAME_SET_STATUS = "SetChildStatus"  # 9

    def __init__(self):
        self.__IsRunning = False
        self.__Status = None
        self.__ClientSocket = ClientSocket("127.0.0.1", 1669)
        self.__InitializeClientSocket()

    def __InitializeClientSocket(self):
        self.__ClientSocket.SetHeaderSize(4)  # 4 Bytes
        self.__ClientSocket.SetMaximumMessageSize(1024 * 1024)  # 1 MB
        self.__ClientSocket.RegisterCallback(self.__ClientSocket.OnClientConnectEvent, self.OnClientConnect)
        self.__ClientSocket.RegisterCallback(self.__ClientSocket.OnClientSendEvent, self.OnClientSend)
        self.__ClientSocket.RegisterCallback(self.__ClientSocket.OnClientReceiveEvent, self.OnClientReceive)
        self.__ClientSocket.RegisterCallback(self.__ClientSocket.OnClientDisconnectEvent, self.OnClientDisconnect)
        self.__ClientSocket.RegisterCallback(self.__ClientSocket.OnClientWarningEvent, self.OnClientWarning)
        self.__ClientSocket.RegisterCallback(self.__ClientSocket.OnClientExceptionEvent, self.OnClientException)

    def __Post(self, MessageCode, Message):
        MessageCode = len(MessageCode).to_bytes(4, byteorder="little")
        Message = MessageCode + Message
        self.__ClientSocket.Send(Message)

    def __ProcessReceivedMessages(self, Content):
        MessageCode = int.from_bytes(Content[0:2], byteorder="little")
        Message = Content[2:]
        if MessageCode == 5:  # Terminate
            self.Stop()
        elif MessageCode == 8:  # GetChildStatus
            self.PostStatus(self.__Status)

    def Start(self):
        self.__IsRunning = True
        self.__ClientSocket.Connect()

    def Stop(self):
        self.__IsRunning = False
        self.__ClientSocket.Disconnect()
        exit()

    def PostStatus(self, Status):
        self.__Post(9, Status)

    def PostError(self, Error):
        self.__Post(6, Error)

    def PostInfo(self, Information):
        self.__Post(7, Information)

    def PostDetectedFrame(self, FrameBytes):
        self.__Post(4, FrameBytes)

    def OnClientConnect(self, LogMessage):
        self.PostInfo(LogMessage)

    def OnClientSend(self, LogMessage, Content):
        self.PostInfo(LogMessage)

    def OnClientReceive(self, LogMessage, Content):
        self.__ProcessReceivedMessages(Content)
        self.PostInfo(LogMessage)

    def OnClientDisconnect(self, LogMessage):
        self.PostInfo(LogMessage)

    def OnClientWarning(self, LogMessage):
        self.PostInfo(LogMessage)

    def OnClientException(self, LogMessage):
        self.PostInfo(LogMessage)
