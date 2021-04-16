import socket
from threading import Thread


class ClientSocket:
    def __init__(self, Socket, Address):
        self.__InnerSock = Socket
        self.__Address = Address
        self.__IsConnected = True
        self.__HeaderSize = 0
        self.__MaximumMessageSize = 0
        self.__MessageSize = 0
        self.__Message = None

    def GetSocket(self):
        if self.__IsConnected is True:
            return self.__InnerSock
        else:
            return None

    def GetAddress(self):
        if self.__IsConnected is True:
            return self.__Address
        else:
            return None

    def GetHeaderSize(self):
        return self.__HeaderSize

    def SetHeaderSize(self, HeaderSize):
        self.__HeaderSize = HeaderSize

    def GetMaximumMessageSize(self):
        return self.__MaximumMessageSize

    def SetMaximumMessageSize(self, MaximumMessageSize):
        self.__MaximumMessageSize = MaximumMessageSize

    def Send(self, Message):
        try:
            if self.__IsConnected:
                Header = len(Message).to_bytes(4, byteorder="little")
                Packet = Header + Message
                self.__InnerSock.send(Packet)
        except Exception as e:
            print("Error at Send method: {}".format(e.__str__()))
            self.Disconnect()

    def StartReceiver(self):
        T = Thread(target=self.__Receiver)
        T.start()

    def __Receiver(self):
        try:
            if self.__IsConnected:
                HeaderBytes = self.__InnerSock.recv(self.__HeaderSize)
                self.__MessageSize = int.from_bytes(HeaderBytes, byteorder="little")
                if self.__MessageSize <= 0 or self.__MessageSize >= self.__MaximumMessageSize:
                    self.Disconnect()
                else:
                    self.__Message = self.__InnerSock.recv(self.__MessageSize)
                    print("Received: ", self.__Message)
                    self.__Receiver()
        except Exception as e:
            print("Error at Receiver method: {}".format(e.__str__()))
            self.Disconnect()

    def Disconnect(self):
        if self.__IsConnected:
            self.__IsConnected = False
            self.__InnerSock.shutdown(socket.SHUT_RDWR)
            self.__InnerSock.close()
