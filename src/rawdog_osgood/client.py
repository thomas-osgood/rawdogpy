import base64
import json
import socket
import struct

DEFAULT_ENCODING = "utf-8"

KEY_ADDL = "Addldata"
KEY_AGENT = "Agentname"
KEY_ENDPOINT = "Endpoint"

MAX_PORT = (1 << 16) - 1
MIN_PORT = 1

SIZE_PACKET_FMT = ">HQ"

class RawdogClientBase:
    """
    class that implements the Rawdog TCP communication protocol. 

    this has functions to both transmit to and receive information
    from a Rawdog server, along with some basic metadata functions.
    """

    def __init__(self, server_addr:str, **kwargs):

        if not(isinstance(server_addr,str)):
            raise TypeError(f"server_addr must be a string. got {type(server_addr)}")
        
        s_timeout = kwargs.get("send_timeout", 10)

        if not(isinstance(s_timeout,int)):
            raise TypeError(f"send_timeout must be an int. got {type(s_timeout)}")
        elif s_timeout < 1:
            raise ValueError("send_timeout must be a positive int.")

        self.__agent_name = "client"
        self.__srvaddr = server_addr
        self.__send_timeout = s_timeout

        return
    
    def generic_md(self, endpoint:int):
        """
        function designed to build and return generic metadata
        for the given endpoint.

        generic md format:

            {
                "Agentname": string,
                "Endpoint": integer,
                "Addldata": string
            }
        """
        md = dict()
        err = None

        try:
            if not(isinstance(endpoint,int)):
                raise TypeError(f"endpoint must be an int. got {type(endpoint)}")
            
            md[KEY_AGENT] = self.__agent_name
            md[KEY_ENDPOINT]= endpoint
            md[KEY_ADDL]= str()

        except Exception as ex:
            err = ex

        return (md, err)
    
    def recv(self, conn:socket.socket):
        """
        function designed to receive data from
        the server.
        """
        err = None
        metadata = dict()
        data = bytes()

        # get the size of the remaining pieces
        # of the packet being transmitted to the client.
        size_packet = conn.recv(10)
        meta_size, data_size = struct.unpack(SIZE_PACKET_FMT, size_packet)

        # raise an error if no data is being transmitted
        # to the client.
        if (meta_size < 1) and (data_size < 1):
            raise ValueError("no data in the main body")

        # get the metadata packet.
        if meta_size > 0:
            metadata = conn.recv(meta_size)
        else:
            metadata = ""
        
        # get the data packet.
        if data_size > 0:
            data = conn.recv(data_size)

        return (metadata, data, err)
    
    def send(self, headers:dict, message:bytes):
        """
        function designed to transmit data to
        the server.
        """
        data_size = int()
        err = None
        meta_size = int()
        r_dat = bytes()
        r_md = dict()

        try:
            if not(isinstance(headers,dict)):
                raise TypeError(f"headers must be a dict. got {type(headers)}")
            
            if isinstance(message,str):
                message = message.encode(DEFAULT_ENCODING)
            elif not(isinstance(message,bytes)):
                raise TypeError(f"message must be bytes. got {type(message)}")

            # json-encode the metadata.
            metadata = json.dumps(headers).encode(DEFAULT_ENCODING)
            # base64-encode the message.
            message = base64.b64encode(message)

            # get the sizes of both the metadata and
            # data being transmitted.
            meta_size = len(metadata)
            data_size = len(message)

            # format the payload that will be transmitted
            # to the server.
            payload = struct.pack(f"{SIZE_PACKET_FMT}{meta_size}s{data_size}s", meta_size, data_size, metadata, message)

            # open a connection to the server and transmit
            # the payload.
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conn:
                # set send timeout.
                #
                # reference: https://docs.python.org/3/library/socket.html#socket.socket.settimeout
                conn.settimeout(self.__send_timeout)
                # connect to server.
                conn.connect((self.__srvaddr, self.__srvport))
                # transmit data.
                conn.sendall(payload)

                r_md, r_dat, err = self.recv(conn=conn)
                if err:
                    raise err

        except Exception as ex:
            err = ex

        return (r_md, r_dat, err)
    
class RawdogClientTcp(RawdogClientBase):
    """
    rawdog client class designed to communicate with a server
    being hosted on a TCP socket.
    """

    def __init__(self, server_addr, server_port, **kwargs):
        super().__init__(server_addr, server_port, **kwargs)

        if not(isinstance(server_port,int)):
            raise TypeError(f"server_port must be an int. got {type(server_port)}")
        elif not(MIN_PORT <= server_port <= MAX_PORT):
            raise ValueError(f"server_port must be within range {MIN_PORT} - {MAX_PORT}")
        
        self.__srvport = server_port
        
        return
    
class RawdogClientUnix(RawdogClientBase):
    """
    rawdog client class designed to communicate with a server
    being hosted on a unix socket.
    """
    
    def __init__(self, server_addr, **kwargs):
        super().__init__(server_addr, **kwargs)
        return

def main():
    return

if __name__ == "__main__":
    main()