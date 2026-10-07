class VoiceInput:
    def collect(self, transcript):
        return transcript
class ImageUpload:
    def collect(self, path):
        return path
class SearchResultView:
    def display(self, response):
        for result in response['results']:
            p = result['product']
            print(f"{p['id']:2} | {p['name']:<24} | ${p['price']:6.2f} | score={result['score']:.6f}")
        if response['order']:
            o = response['order']
            print(f"Order {o['order_id']} | {o['status']} | total=${o['total']:.2f}")
        elif not response['results']:
            print('No results')
class SearchUI:
    def __init__(self, query_service, speech_service, image_service, search_service):
        self.query_service, self.speech_service = query_service, speech_service
        self.image_service, self.search_service = image_service, search_service
        self.voice_input, self.image_upload, self.view = VoiceInput(), ImageUpload(), SearchResultView()
    def submit(self, mode, value, customer_id='C001', top_k=5, filters=None, image_path=None, text_weight=0.5):
        if mode == 'text':
            query = self.query_service.text_query(value, customer_id=customer_id, filters=filters)
        elif mode == 'voice':
            transcript = self.speech_service.transcribe(self.voice_input.collect(value))
            query = self.query_service.voice_query(transcript, customer_id, filters)
        elif mode == 'image':
            vector = self.image_service.encode(self.image_upload.collect(value))
            query = self.query_service.image_query(vector, customer_id, filters)
        elif mode == 'multimodal':
            vector = self.image_service.encode(self.image_upload.collect(image_path))
            query = self.query_service.multimodal_query(value, vector, customer_id, filters, text_weight)
        else:
            raise ValueError('Supported modes: text, voice, image, multimodal')
        response = self.search_service.search(query, top_k)
        if mode == 'voice':
            response['processing'].insert(0,'simulated speech-to-text')
        return response

    def submit_audio(self, audio, customer_id='C001', top_k=5, filters=None):
        recognition = self.speech_service.transcribe_audio(audio)
        query = self.query_service.voice_query(recognition['text'], customer_id, filters)
        response = self.search_service.search(query, top_k)
        response['processing'].insert(0, 'real audio → Vosk offline speech-to-text')
        response['speech'] = recognition
        return response
