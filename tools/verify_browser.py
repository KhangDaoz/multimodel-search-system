"""Browser acceptance + screenshots; synthetic WAV feeds Chromium's virtual microphone."""
import json
import os
from pathlib import Path
import sys
import threading
from http.server import ThreadingHTTPServer
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from playwright.sync_api import sync_playwright
from main import build_ui
from presentation.web_server import make_handler

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
server = ThreadingHTTPServer(('127.0.0.1',0),make_handler(build_ui()))
thread = threading.Thread(target=server.serve_forever,daemon=True); thread.start()
base = f'http://127.0.0.1:{server.server_port}'
checks = []; errors = []
def check(name,condition):
    if not condition: raise AssertionError(name)
    checks.append(name)

try:
    with sync_playwright() as p:
        executable = os.environ.get('CHROME_PATH')
        if not executable:
            candidates = list(Path.home().glob('.cache/puppeteer/chrome/*/chrome-linux64/chrome'))
            executable = str(candidates[-1]) if candidates else None
        browser = p.chromium.launch(executable_path=executable,headless=True,args=[
            '--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream',
            '--use-file-for-fake-audio-capture='+str(ROOT/'tests/fixtures/blue_shoes.wav')])
        context = browser.new_context(viewport={'width':1440,'height':1000},permissions=['microphone'])
        page = context.new_page(); page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto(base); page.wait_for_selector('.product-card'); page.wait_for_function("document.querySelector('#record').disabled === false")
        check('15 photographed catalog products',page.locator('.product-card').count() == 15)
        page.screenshot(path='reports/figures/storefront-desktop.png',full_page=True)
        page.locator('#filter-category').select_option('shirt'); page.locator('#filter-stock').check(); page.locator('#apply-filters').click()
        page.wait_for_function("document.querySelectorAll('.product-card').length === 4")
        check('catalog category and stock filter',page.locator('.product-card').count() == 4)
        page.locator('#reset').click(); page.wait_for_function("document.querySelectorAll('.product-card').length === 15")
        page.locator('#query').fill('blue shoes'); page.locator('#search').evaluate('(form) => form.requestSubmit()')
        page.wait_for_function("document.querySelector('#status').textContent.includes('matches')")
        check('text relevance', 'Puma' in page.locator('.product-title-row h3').first.inner_text())
        page.locator('#collection').screenshot(path='reports/figures/storefront-search.png')
        page.locator('.product-details').first.click(); page.wait_for_selector('#product-modal.show')
        check('photo/details modal', 'Puma' in page.locator('#detail-title').inner_text())
        page.locator('#detail-add').click(); check('add to bag',page.locator('#bag-count').inner_text() == '1')
        page.locator('#product-modal .btn-close').click(); page.wait_for_selector('#product-modal',state='hidden')
        page.locator('#bag-open').click(); page.wait_for_selector('#bag-modal.show')
        check('shopping bag subtotal',page.locator('#bag-total').inner_text() == '$89.99')
        page.locator('#bag-modal .btn-close').click(); page.reload(); page.wait_for_selector('.product-card')
        check('bag persists across reload',page.locator('#bag-count').inner_text() == '1')
        page.locator('[data-mode="image"]').click(); page.locator('#image').set_input_files('data/images/p05.png')
        page.locator('#search').evaluate('(form) => form.requestSubmit()'); page.wait_for_function("document.querySelector('#status').textContent.includes('matches')")
        check('actual photo upload','Sports Sneakers Off White Red' in page.locator('.product-title-row h3').first.inner_text())
        page.locator('[data-mode="multimodal"]').click(); page.locator('#query').fill('blue shoes'); page.locator('#image').set_input_files('data/images/p03.png')
        page.locator('#text-weight').fill('0.7'); page.locator('#text-weight').dispatch_event('input')
        page.locator('#search').evaluate('(form) => form.requestSubmit()'); page.wait_for_selector('.product-signals')
        check('fusion result and contributions','Puma' in page.locator('.product-title-row h3').first.inner_text())
        page.locator('#collection').screenshot(path='reports/figures/storefront-fusion.png')
        page.locator('[data-mode="voice"]').click(); check('voice has no typed transcript input',not page.locator('#text-input').is_visible())
        page.locator('#audio-file').set_input_files('tests/fixtures/blue_shoes.wav'); page.wait_for_selector('#transcript:not([hidden])',timeout=30000)
        check('real uploaded audio recognized','blue shoes' in page.locator('#transcript').inner_text())
        check('voice ranks correct photo','Puma' in page.locator('.product-title-row h3').first.inner_text())
        page.locator('#collection').screenshot(path='reports/figures/storefront-voice.png')
        page.locator('#record').click(); page.wait_for_selector('#record.recording'); page.wait_for_timeout(3000); page.locator('#record').click()
        page.wait_for_selector('#transcript:not([hidden])',timeout=30000)
        check('MediaRecorder virtual microphone → real Vosk recognizer','blue shoes' in page.locator('#transcript').inner_text())
        check('microphone tracks released',page.evaluate('microphoneStream === null'))
        page.locator('#reset').click(); page.locator('#query').fill('spaceship'); page.locator('#search').evaluate('(f) => f.requestSubmit()')
        page.wait_for_selector('#empty:not([hidden])'); check('empty result state',page.locator('.product-card').count() == 0)
        page.locator('#orders-link').click(); page.wait_for_selector('.order-card'); check('latest order','20261001' in page.locator('.order-card').inner_text())
        page.set_viewport_size({'width':390,'height':844}); page.locator('#reset').click(); page.wait_for_function("document.querySelectorAll('.product-card').length === 15")
        page.screenshot(path='reports/figures/storefront-mobile.png',full_page=True)
        check('mobile has no horizontal overflow',page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
        page.set_viewport_size({'width':1440,'height':1000}); check('desktop has no horizontal overflow',page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
        check('no JavaScript exceptions',not errors)
        browser.close()
    result = {'passed':len(checks),'checks':checks,'javascript_errors':errors,'microphone_scope':'Chromium virtual device fed by synthetic eSpeak WAV; real MediaRecorder/audio decoding/Vosk run without STT mocks. Human microphone and accent accuracy require manual trials.'}
    Path('results/browser-verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
finally:
    server.shutdown(); server.server_close(); thread.join()
