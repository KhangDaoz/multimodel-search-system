import argparse
import json
from pathlib import Path
from application.query_service import QueryService
from application.speech_service import SpeechService
from application.speech_service import SpeechUnavailable
from application.image_service import ImageService
from application.search_service import SearchService
from application.ranking_service import RankingService
from data.product_repository import ProductRepository
from data.order_repository import OrderRepository
from data.vector_index import VectorIndex
from presentation.search_ui import SearchUI

def build_ui():
    repository, encoder = ProductRepository(), ImageService()
    index = VectorIndex({p['id']:encoder.encode(repository.image_path(p)) for p in repository.all_products()})
    service = SearchService(repository,index,RankingService(),OrderRepository())
    return SearchUI(QueryService(),SpeechService(),encoder,service)

def main():
    parser = argparse.ArgumentParser(description='Assignment 06 multimodal search prototype')
    launch = parser.add_mutually_exclusive_group()
    launch.add_argument('--web', action='store_true', help='Start the browser interface (default)')
    launch.add_argument('--cli', action='store_true', help='Run the command-line demonstration')
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--mode', choices=['text','voice','image','multimodal','audio'])
    parser.add_argument('--query')
    parser.add_argument('--image', help='Image path for multimodal search')
    parser.add_argument('--text-weight', type=float, default=0.5)
    parser.add_argument('--customer', default='C001')
    parser.add_argument('--top-k',type=int,default=5)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    if args.top_k < 1: parser.error('--top-k must be positive')
    if args.mode and not args.query: parser.error('--query is required with --mode')
    if args.mode == 'multimodal' and not args.image: parser.error('--image is required with --mode multimodal')
    if not 0 <= args.port <= 65535: parser.error('--port must be between 0 and 65535')
    ui = build_ui()
    if args.web or not (args.cli or args.mode or args.json):
        from presentation.web_server import serve
        serve(ui, args.port)
        return
    inputs = [(args.mode,args.query)] if args.mode else [('text','black shoes'),('voice','find running shoes'),('image',str(Path(__file__).parent/'data/images/p01.png')),('text','find order O001')]
    responses=[]
    for mode,value in inputs:
        try:
            response = ui.submit_audio(Path(value).read_bytes(),args.customer,args.top_k) if mode == 'audio' else ui.submit(mode,value,args.customer,args.top_k,image_path=args.image,text_weight=args.text_weight)
        except (ValueError,OSError,SpeechUnavailable) as error: parser.error(str(error))
        response['input'] = {'mode':mode,'value':value}
        responses.append(response)
        if not args.json:
            print(f'\nINPUT [{mode}]: {value}')
            print('PROCESSING: '+' -> '.join(response['processing']))
            if mode in ('image','multimodal'):print('QUERY REPRESENTATION: '+mode+'; embedding dimension='+str(len(response['query']['embedding'])))
            else: print('QUERY REPRESENTATION: '+response['query']['query'])
            ui.view.display(response)
    if args.json: print(json.dumps(responses,indent=2))
if __name__ == '__main__': main()
