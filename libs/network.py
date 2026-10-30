from . import linxrtcgui
class Network:


    @staticmethod 
    def validate(host,port,remember=False):

       
        if not host:
            raise linxrtcgui("invalid host ip / name")
        
        if not port: 
            port = int(port)
            if port_int > 65535:
                raise linxrtcgui("invalid port spacification")
        
    
        
        return True


            
