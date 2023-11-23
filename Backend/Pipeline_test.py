import websocket
# ws = create_connection("wss://relay.uas.unexceptional.dev/relay/images/outbound")
ws = websocket.create_connection("wss://asdjsajkdsad")
print ("Receiving...")
result =  ws.recv()
print ("Received: ", result)
ws.close()