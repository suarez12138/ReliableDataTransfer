from USocket import UnreliableSocket
import threading
import time
from packet import Packet


class RDTSocket(UnreliableSocket):
    """
    The functions with which you are to build your RDT.
    -   recvfrom(bufsize)->bytes, addr
    -   sendto(bytes, address)
    -   bind(address)

    You can set the mode of the socket.
    -   settimeout(timeout)
    -   setblocking(flag)
    By default, a socket is created in the blocking mode.
    https://docs.python.org/3/library/socket.html#socket-timeouts

    """

    def __init__(self, rate=None, debug=True):
        super().__init__(rate=rate)
        self._rate = rate
        self._send_to = None
        self._recv_from = None
        self.debug = debug
        self.seq = 0
        self.seq_ack = 0

        #############################################################################
        # TODO: ADD YOUR NECESSARY ATTRIBUTES HERE
        #############################################################################
        self.buffer_size = 2048
        self.address = None
        #############################################################################
        #                             END OF YOUR CODE                              #
        #############################################################################

    def accept(self) -> ('RDTSocket', (str, int)):
        """
        Accept a connection. The socket must be bound to an address and listening for
        connections. The return value is a pair (conn, address) where conn is a new
        socket object usable to send and receive data on the connection, and address
        is the address bound to the socket on the other end of the connection.

        This function should be blocking.
        """
        # conn, addr = RDTSocket(self._rate), None
        #############################################################################
        # TODO: YOUR CODE HERE                                                      #
        #############################################################################
        ##receive syn
        self.set_recv_from(super().recvfrom)
        data, addr = self._recv_from(self.buffer_size)
        syn_packet = Packet.from_bytes(data)
        ##need to judge
        self.set_seq_and_ack(syn_packet)
        print(syn_packet)

        ##send syn,ack
        self.set_send_to(self.sendto)
        if syn_packet.SYN == 1:
            syn_ack_packet = Packet(SYN=1, ACK=1,SEQ_ACK=self.seq_ack,SEQ=self.seq)
            self._send_to(syn_ack_packet.to_bytes(), addr)
            print(syn_ack_packet)

        #receive ack
            data2, addr = self._recv_from(self.buffer_size)
            ack_packet=Packet()
            ack_packet = ack_packet.from_bytes(data2)
            ##need to judge
            self.set_seq_and_ack(ack_packet)
            print(ack_packet)
            print(syn_ack_packet==ack_packet)
            if ack_packet.ACK == 1:
                pass
            else:
                pass
            # need to be modified
        #############################################################################
        #                             END OF YOUR CODE                              #
        #############################################################################
        return self, addr

    def connect(self, address: (str, int)):
        """
        Connect to a remote socket at address.
        Corresponds to the process of establishing a connection on the client side.
        """
        syn_packet = Packet(SYN=1)
        self.set_send_to(self.sendto)
        # while True:
        self._send_to(syn_packet.to_bytes(), address)
        # time.sleep(0.1)
        print(syn_packet)

        self.set_recv_from(super().recvfrom)
        data, addr = self._recv_from(self.buffer_size)
        syn_ack_packet = Packet.from_bytes(data)
        self.set_seq_and_ack(syn_ack_packet)
        print(syn_ack_packet)
        # need to add time out situation

        if syn_ack_packet.SYN == 1 and syn_ack_packet == 1:
            ack_packet = Packet(ACK=1, SEQ=self.seq,SEQ_ACK=self.seq_ack)
            self._send_to(ack_packet.to_bytes(), address)
            self.set_address(address)
            print(ack_packet)
        else:
            pass
            # when the packet is wrong

    def recv(self, bufsize: int) -> bytes:
        """
        Receive data from the socket.
        The return value is a bytes object representing the data received.
        The maximum amount of data to be received at once is specified by bufsize.

        Note that ONLY data send by the peer should be accepted.
        In other words, if someone else sends data to you from another address,
        it MUST NOT affect the data returned by this function.
        """
        # data = None
        # assert self._recv_from, "Connection not established yet. Use recvfrom instead."
        #############################################################################
        # TODO: YOUR CODE HERE                                                      #
        #############################################################################
        packet=Packet.from_bytes(self._recv_from(bufsize)[0])
        data = packet.PAYLOAD
        self.set_seq_and_ack(packet)
        #############################################################################
        #                             END OF YOUR CODE                              #
        #############################################################################
        return data

    def send(self, bytes: bytes):
        """
        Send data to the socket.
        The socket must be connected to a remote socket, i.e. self._send_to must not be none.
        """
        assert self._send_to, "Connection not established yet. Use sendto instead."
        #############################################################################
        # TODO: YOUR CODE HERE                                                      #
        #############################################################################

        self._send_to(Packet(SEQ=self.seq,ACK=self.ack,data=bytes).to_bytes(), self.address)
        #need to be modified
        #############################################################################
        #                             END OF YOUR CODE                              #
        #############################################################################

    def close(self):
        """
        Finish the connection and release resources. For simplicity, assume that
        after a socket is closed, neither futher sends nor receives are allowed.
        """
        #############################################################################
        # TODO: YOUR CODE HERE                                                      #
        #############################################################################

        #############################################################################
        #                             END OF YOUR CODE                              #
        #############################################################################
        super().close()

    def set_send_to(self, send_to):
        self._send_to = send_to

    def set_recv_from(self, recv_from):
        self._recv_from = recv_from

    def set_address(self, address):
        self.address = address

    def set_buffer_size(self, bufsize):
        self.buffer_size = bufsize

    def set_seq_and_ack(self, packet: Packet):
        self.seq = packet.SEQ_ACK
        self.seq_ack += packet.LEN


"""
You can define additional functions and classes to do thing such as packing/unpacking packets, or threading.

"""

"""
Reliable Data Transfer Segment

Segment Format:

|0 1 2 3 4 5 6 7 8|0 1 2 3 4 5 6 7 8|0 1 2 3 4 5 6 7 8|0 1 2 3 4 5 6 7 8| 
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|           (NO USE)          |S|F|A|              CHECKSUM             |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                              SEQ                                      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                            SEQ ACK                                    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                              LEN                                      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                                       |
/                            PAYLOAD                                    /
/                                                                       /
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


Flags:
 - S-SYN                      Synchronize
 - F-FIN                      Finish
 - A-ACK                      Acknowledge

Ranges:
 - Payload Length           0 - 2^32  (append zeros to the end if length < 1440)
 - Sequence Number          0 - 2^32
 - Acknowledgement Number   0 - 2^32
 - CHECKSUM                 0 - 2^16


Size of sender's window     16
"""


def checksum(payload):
    sum = 0
    for byte in payload:
        sum += byte
    sum = -(sum % 256)
    return sum & 0xff


if __name__ == '__main__':
    import struct

    payload = 'akjdfakdfjsdaf'
    o = checksum(bytes(payload.encode("UTF-8")))
    print(o)
