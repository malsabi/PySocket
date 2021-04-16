import socket
# Synchronized Socket, That can handle it self if errors were found, reconnect to server if a shutdown occurs.
# A general Client Socket class that contains the public member Connect, Send, Disconnect,
# GetBufferSize, SetBufferSize, GetHeaderSize, SetHeaderSize, SetMaximumMessage, GetMaximumMessage, IsConnected.
# RegisterCallback, UnregisterCallback
# and has the private members StartReceiver, Receiver, Event, InnerBufferSize, InnerHeaderSize, MaximumMessageSize, MessageSize,
# InnerIsConnected, InnerSock.
import time
from threading import Thread


class ClientSocket:
    OnClientConnectEvent = "OnClientConnect"
    OnClientReceiveEvent = "OnClientReceive"
    OnClientSendEvent = "OnClientSend"
    OnClientDisconnectEvent = "OnClientDisconnect"
    OnClientReconnectEvent = "OnClientReconnect"
    OnClientWarningEvent = "OnClientWarning"
    OnClientExceptionEvent = "OnClientException"

    def __init__(self, Host, Port):
        self.Port = Port
        self.Host = Host
        self.__InnerHeaderSize = 0
        self.__MaximumMessageSize = 0
        self.__MessageSize = 0
        self.__Message = None
        self.__InnerIsConnected = False
        self.__InnerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__Observables = {}

    def RegisterCallback(self, Name, CallbackMethod):
        if not self.__Observables.__contains__(Name):
            self.__Observables[Name] = CallbackMethod
        else:
            self.__Event(self.OnClientWarningEvent, "Failed to register the callback, it's already registered", None)

    def UnregisterCallback(self, Name):
        if self.__Observables.__contains__(Name):
            self.__Observables.pop(Name)
        else:
            self.__Event(self.OnClientWarningEvent, "Failed to unregister the callback, it's not registered", None)

    def GetHeaderSize(self):
        return self.__InnerHeaderSize

    def SetHeaderSize(self, HeaderSize):
        self.__InnerHeaderSize = HeaderSize

    def GetMaximumMessageSize(self):
        return self.__MaximumMessageSize

    def SetMaximumMessageSize(self, MaximumMessageSize):
        self.__MaximumMessageSize = MaximumMessageSize

    def IsConnected(self):
        return self.__InnerIsConnected

    def Connect(self):
        T = Thread(target=self.__AttemptToConnect)
        T.start()

    def Send(self, Message):
        try:
            if self.__InnerIsConnected:
                Header = len(Message).to_bytes(4, byteorder="little")
                Packet = Header + Message
                self.__InnerSock.send(Packet)
                self.__Event(self.OnClientReceiveEvent, "Client[{0}:{1}] Sent successfully".format(self.Host, self.Port), len(Packet))
        except Exception as e:
            self.__Event(self.OnClientExceptionEvent, "Error at Send method: {}".format(e.__str__()), None)
            self.Disconnect()

    def Disconnect(self):
        if self.__InnerIsConnected:
            self.__InnerIsConnected = False
            self.__InnerSock.shutdown(2)
            self.__InnerSock.close()
            self.__Event(self.OnClientDisconnectEvent, "Client[{0}:{1}] Disconnected successfully".format(self.Host, self.Port), None)

    def __AttemptToConnect(self):
        while True:
            if not self.__InnerIsConnected:
                try:
                    self.__InnerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.__InnerSock.connect((self.Host, self.Port))
                    self.__InnerIsConnected = True
                    self.__StartReceiver()
                    self.__Event(self.OnClientConnectEvent, "Client[{0}:{1}] Connected successfully".format(self.Host, self.Port), None)
                except Exception as e:
                    self.__Event(self.OnClientExceptionEvent, "Error at AttemptToConnect method: {}".format(e.__str__()), None)
                    self.Disconnect()
                    self.__Event(self.OnClientReconnectEvent, "Attempting to reconnect", None)
            time.sleep(1)

    def __StartReceiver(self):
        T = Thread(target=self.__Receiver)
        T.start()

    def __Receiver(self):
        try:
            if self.__InnerIsConnected:
                HeaderBytes = self.__InnerSock.recv(self.__InnerHeaderSize)
                self.__MessageSize = int.from_bytes(HeaderBytes, byteorder="little")
                if self.__MessageSize >= self.__MaximumMessageSize:
                    self.Disconnect()
                else:
                    self.__Message = self.__InnerSock.recv(self.__MessageSize)
                    self.__Event(self.OnClientReceiveEvent, "Client[{0}:{1}] Received successfully".format(self.Host, self.Port), self.__Message)
                    self.__Receiver()
        except Exception as e:
            self.__Event(self.OnClientExceptionEvent, "Error at Receiver method: {}".format(e.__str__()), None)
            self.Disconnect()

    def __Event(self, EventName, LogMessage, Content):
        if self.__Observables.__contains__(EventName):
            if EventName == self.OnClientReceiveEvent:
                self.__Observables[EventName](LogMessage, Content)
            elif EventName == self.OnClientSendEvent:
                self.__Observables[EventName](LogMessage, Content)
            else:
                self.__Observables[EventName](LogMessage)
        else:
            self.__Event(self.OnClientWarningEvent, "Failed to fire the event", None)