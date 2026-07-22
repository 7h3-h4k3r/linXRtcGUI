from . import linxrtcgui
class Network:


    @staticmethod 
    def validate(host,port,timeout,remember=False):

       
        if not host:
            raise linxrtcgui("invalid host ip / name")
        
        if not port: 
            port = int(port)
            if port_int > 65535:
                raise linxrtcgui("invalid port spacification")
        
        if not timeout:

            timeout = int(timeout)
            if timeout > 300:
                raise linxtcgui("invalid timeout 5 min only allowed")
        
        return True


            
