def create_interupt_handler(recorder):
    def handle_interrupt(sig, frame):
        print("Ctrl + C is pressed")
        recorder.buffer.put(None)
        recorder.state = -1
        
    return handle_interrupt