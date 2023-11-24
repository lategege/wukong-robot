import websockets,ssl
import json
import time 
import asyncio

class funASRWss(object):

    def __init__(self, url):
        self.url = url 
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
  

    async def sendData(self,wav_path):
      ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
      ssl_context.check_hostname = False
      ssl_context.verify_mode = ssl.CERT_NONE
      async with websockets.connect(self.url, subprotocols=["binary"], ping_interval=None, ssl=ssl_context) as self.wss:
        #deal wave_file
        result = None
        sample_rate  = 16000
        wav_name = "pcm_data"
        wav_format = "pcm"
        pre_message = json.dumps({"mode": "offline", "chunk_size": "5, 10, 5", "chunk_interval": 10, "audio_fs":sample_rate,
                          "wav_name": wav_name, "wav_format": wav_format, "is_speaking": True, "hotwords":"", "itn": True})
        if self.wss is not None:
            if wav_path.endswith(".pcm"):
                with open(wav_path, "rb") as f:
                   audio_bytes = f.read()
            elif wav_path.endswith(".wav"):
                import wave
                with wave.open(wav_path, "rb") as wav_file:
                     sample_rate = wav_file.getframerate()
                     frames = wav_file.readframes(wav_file.getnframes())
                     audio_bytes = bytes(frames)
            else:
               wav_format = "others"
               with open(wav_path, "rb") as f:
                audio_bytes = f.read()
            # stride  = int(chunk_size/1000*16000*2)
            stride = int(192000)
            chunk_num = (len(audio_bytes) - 1) // stride + 1
            #send config json
            await self.wss.send(pre_message)
            print(f"Sent: {pre_message}")
            for i in range(chunk_num):
               beg = i * stride
               data = audio_bytes[beg:beg + stride]
               message = data
               #voices.put(message)
               await self.wss.send(message)
               if i == chunk_num - 1:
                   message = json.dumps({"is_speaking": False})
                   #voices.put(message)
                   await self.wss.send(message)
                   #receive msg
                   recv_msg = await self.wss.recv()
                   recv_msg = json.loads(recv_msg)
                   result = recv_msg['text'] 
                   print("reslut is: " +result)
               sleep_duration = 0.001 
               asyncio.sleep(sleep_duration)
            
        else:
            print("Connection not established.")
        return result  

    def asr(self, wave_file):
       return self.loop.run_until_complete(self.sendData(wave_file))
    