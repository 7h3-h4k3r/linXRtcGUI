from src.themeClass import Theme
class routeR:

    @staticmethod
    def group_message_send(chatplace,handler,msg):
        result = msg.split(":")
        new_message = ' '.join(result[1:])
        other_message=f"{result[0].strip()}\n{new_message.strip()}"
        chatplace.add_message(handler,other_message)

    @staticmethod
    def set_latency(latency ,right_panel):

        value= None
        
        if latency <= 50:
            value=("Excellent", Theme.GREEN)
        elif latency <= 100:
            value=("Good", Theme.ORANGE)
        elif latency <= 200:
            value=("Fair", Theme.YELLOW)
        elif latency <= 300:
            value=("Poor", Theme.BLUE)
        else:
            value=("Very Poor",Theme.RED)

        right_panel.update_info(
            connection_quality=(value[0], value[1])
        )

