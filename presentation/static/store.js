'use strict';
const $ = id => document.getElementById(id);
const money = value => new Intl.NumberFormat('en-US', {style:'currency', currency:'USD'}).format(value);
const modal = new bootstrap.Modal($('product-modal'));
const bagModal = new bootstrap.Modal($('bag-modal'));
const toast = new bootstrap.Toast($('bag-toast'));
let mode = 'text', previewURL = null, currentProducts = [], catalog = [], requestVersion = 0;
let recording = null, recordTimer = null, microphoneStream = null, voiceReady = false, recordingVersion = 0, requestingMicrophone = false;
let bag = {};
try { const saved = JSON.parse(localStorage.getItem('forme-bag-v02') || '{}'); if (saved && typeof saved === 'object' && !Array.isArray(saved)) bag = saved; } catch { bag = {}; }

function element(tag, text = '', className = '') {
  const node = document.createElement(tag); node.textContent = text; node.className = className; return node;
}
async function request(path, options) {
  const response = await fetch(path, options); const data = await response.json();
  if (!response.ok) throw Error(data.error || 'Unable to complete this request.'); return data;
}
function filters() {
  const price = id => $(id).value === '' ? null : Number($(id).value);
  const selected = {category:$('filter-category').value || null, min_price:price('filter-min'), max_price:price('filter-max'), in_stock:$('filter-stock').checked};
  if (selected.min_price !== null && selected.max_price !== null && selected.min_price >= selected.max_price) throw Error('Minimum price must be below the maximum price.');
  return selected;
}
function stopRecording(cancel = false) {
  clearTimeout(recordTimer);
  if (cancel) recordingVersion++;
  if (recording && recording.state !== 'inactive') recording.stop();
  if (microphoneStream) microphoneStream.getTracks().forEach(track => track.stop());
  microphoneStream = null;
  $('record').classList.remove('recording'); $('record').textContent = 'Start recording';
}
function setMode(next) {
  stopRecording(true); mode = next; requestVersion++; busy(false); clearError();
  document.querySelectorAll('[data-mode]').forEach(button => { button.classList.toggle('active', button.dataset.mode === mode); button.setAttribute('aria-pressed', String(button.dataset.mode === mode)); });
  $('text-input').hidden = mode === 'image' || mode === 'voice';
  $('voice-input').hidden = mode !== 'voice';
  $('image-input').hidden = mode !== 'image' && mode !== 'multimodal';
  $('fusion-control').hidden = mode !== 'multimodal';
  $('query').required = mode === 'text' || mode === 'multimodal';
  $('image').required = mode === 'image' || mode === 'multimodal';
  $('submit').hidden = mode === 'voice';
  $('mode-hint').textContent = mode === 'voice' ? 'Record or upload real speech. We search automatically after recognition.' : mode === 'multimodal' ? 'Combine a picture with product keywords. Adjust how much each matters.' : mode === 'image' ? 'PNG, JPEG, or WebP · up to 5 MB. Try a product sample from its details.' : 'Search by colour, category, brand, or a price limit.';
  updateVoiceState();
}
function busy(value) {
  $('submit').disabled = value; $('spinner').hidden = !value; $('submit-label').textContent = value ? 'Searching…' : 'Search ↗';
  $('record').disabled = value || !voiceReady || requestingMicrophone;
  $('audio-file').disabled = value || !voiceReady;
}
function clearError() { $('error').hidden = true; }
function showError(error) { $('error').textContent = error.message; $('error').hidden = false; $('status').textContent = 'Unable to complete the request.'; }
function fileData(file) {
  return new Promise((resolve,reject) => { const reader = new FileReader(); reader.onload = () => resolve(reader.result.split(',')[1]); reader.onerror = () => reject(Error('Cannot read this file.')); reader.readAsDataURL(file); });
}
function saveBag() { try { localStorage.setItem('forme-bag-v02', JSON.stringify(bag)); } catch { /* Bag remains usable for this session. */ } renderBag(); }
function addToBag(id) {
  const product = catalog.find(p => p.id === id); if (!product || !product.stock) return;
  const quantity = Number(bag[id]) || 0;
  if (quantity >= product.stock) { $('bag-toast-message').textContent = 'You have reached the available quantity.'; toast.show(); return; }
  bag[id] = quantity + 1; saveBag(); $('bag-toast-message').textContent = product.name + ' added to your bag'; toast.show();
}
function renderBag() {
  $('bag-items').replaceChildren(); let count = 0, total = 0;
  for (const [id, raw] of Object.entries(bag)) {
    const product = catalog.find(p => p.id === Number(id));
    if (!product || !Number.isInteger(raw) || raw < 1 || !product.stock) { delete bag[id]; continue; }
    const quantity = Math.min(raw,product.stock); bag[id] = quantity; count += quantity; total += quantity * product.price;
    const row = element('div','','bag-item'); const image = element('img'); image.src = '/api/product-images/' + id; image.alt = product.name;
    const info = element('div'); info.append(element('h3',product.name),element('p',money(product.price)));
    const controls = element('div','','bag-controls');
    for (const [label,delta] of [['−',-1],['+',1]]) {
      const button = element('button',label); button.type = 'button'; button.setAttribute('aria-label',(delta < 0 ? 'Decrease ' : 'Increase ') + product.name);
      button.disabled = delta > 0 && quantity >= product.stock;
      button.onclick = () => { bag[id] = quantity + delta; if (!bag[id]) delete bag[id]; saveBag(); };
      controls.append(button); if (delta < 0) controls.append(element('span',String(quantity)));
    }
    row.append(image,info,controls); $('bag-items').append(row);
  }
  if (!count) $('bag-items').append(element('p','Your bag is empty. Find something you love.','hint'));
  $('bag-count').textContent = String(count); $('bag-total').textContent = money(total);
}
async function showDetails(id) {
  try {
    const product = await request('/api/products/' + id);
    $('detail-title').textContent = product.name; $('detail-category').textContent = product.brand + ' / ' + product.category;
    $('detail-price').textContent = money(product.price); $('detail-description').textContent = product.description;
    $('detail-image').src = '/api/product-images/' + product.id; $('detail-image').alt = product.name;
    $('detail-download').href = '/api/product-images/' + product.id; $('detail-download').download = 'product-' + product.id + '.png';
    $('detail-fields').replaceChildren();
    for (const [label,value] of [['Colour',product.color],['Stock',product.stock ? product.stock + ' available' : 'Out of stock'],['Rating', product.rating + ' / 5 · sample reviews'],['Product ID',product.id]]) $('detail-fields').append(element('dt',label),element('dd',String(value)));
    $('detail-shipping').textContent = product.shipping + ' · ' + product.returns;
    $('detail-add').disabled = !product.stock; $('detail-add').textContent = product.stock ? 'Add to bag' : 'Out of stock'; $('detail-add').onclick = () => addToBag(product.id);
    modal.show();
  } catch (error) { showError(error); }
}
function renderProducts() {
  $('results').replaceChildren(); const products = [...currentProducts];
  if ($('sort').value === 'price-low') products.sort((a,b) => a.product.price - b.product.price);
  if ($('sort').value === 'price-high') products.sort((a,b) => b.product.price - a.product.price);
  for (const result of products) {
    const p = result.product; const column = element('div','','col-6 col-md-4 col-lg-3'); const card = element('article','','card product-card');
    const photo = element('div','','product-photo'); const img = element('img'); img.src = '/api/product-images/' + p.id; img.alt = p.name; img.loading = 'lazy'; photo.append(img);
    if (result.rank) photo.append(element('span','#' + result.rank + ' MATCH','rank-label'));
    if (!p.stock) photo.append(element('span','Out of stock','stock-badge'));
    const body = element('div','','card-body'); body.append(element('div',p.brand,'product-brand'));
    const title = element('div','','product-title-row'); title.append(element('h3',p.name),element('span',money(p.price),'product-price')); body.append(title);
    body.append(element('div','★ ' + p.rating.toFixed(1) + ' · ' + p.reviews_count + ' sample reviews','product-rating'));
    if (result.score !== undefined) body.append(element('div','Match score · ' + result.score.toFixed(4),'product-score'));
    if (result.signals) body.append(element('div',`Text ${result.signals.text.toFixed(2)} · Image ${result.signals.image.toFixed(2)} · Weight ${Math.round(result.signals.text_weight*100)}% text`,'product-signals'));
    const details = element('button','View details ↗','product-details'); details.type = 'button'; details.setAttribute('aria-label','View details for ' + p.name); details.onclick = () => showDetails(p.id);
    const add = element('button',p.stock ? 'Add to bag' : 'Sold out','product-add'); add.type = 'button'; add.disabled = !p.stock; add.setAttribute('aria-label','Add ' + p.name + ' to bag'); add.onclick = () => addToBag(p.id);
    body.append(details,add); card.append(photo,body); column.append(card); $('results').append(column);
  }
}
function show(response) {
  currentProducts = response.results.map((result,index) => ({...result,rank:index+1})); $('sort').disabled = Boolean(response.order);
  $('empty').hidden = Boolean(response.results.length || response.order); $('trace-panel').hidden = false; $('trace').textContent = response.processing.join(' → '); renderProducts();
  if (response.speech) { $('transcript').textContent = 'Heard: “' + response.speech.text + '”'; $('transcript').hidden = false; }
  if (response.order) {
    const order = response.order; const column = element('div','','col-12 col-lg-8'); const card = element('article','','card order-card');
    card.append(element('div','YOUR ORDER','eyebrow'),element('h3','Order ' + order.order_id),element('span',order.status,'badge align-self-start my-3'),element('div',money(order.total),'detail-price'),element('p','Customer ' + order.customer_id + ' · ' + order.date));
    for (const item of order.items || []) { const p = catalog.find(p => p.id === item.product_id); card.append(element('div',(p ? p.name : 'Product #' + item.product_id) + ' · Quantity ' + item.quantity + ' · ' + money(item.price) + ' each','order-item')); }
    column.append(card); $('results').append(column); $('status').textContent = 'Your order details';
  } else $('status').textContent = response.results.length ? `${response.results.length} matches · ${response.candidate_count} products considered` : 'No products or orders found';
}
async function search(audio = null) {
  const version = ++requestVersion; busy(true); clearError(); $('status').textContent = audio ? 'Recognizing your speech…' : 'Finding your next favourite…';
  try {
    const payload = {mode,query:$('query').value,customer:$('customer').value,top_k:Number($('limit').value),filters:filters()};
    let path = '/api/search';
    if (audio) { if (audio.size > 5*1024*1024) throw Error('Audio must be smaller than 5 MB.'); payload.audio = await fileData(audio); path = '/api/voice-search'; }
    else if (mode === 'voice') throw Error('Record your voice or upload an audio file to search.');
    else if (mode === 'image' || mode === 'multimodal') { const file = $('image').files[0]; if (!file) throw Error('Please choose a product image.'); if (file.size > 5*1024*1024) throw Error('Image must be smaller than 5 MB.'); payload.image = await fileData(file); payload.text_weight = Number($('text-weight').value); }
    const response = await request(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
    if (version === requestVersion) show(response);
  } catch (error) { if (version === requestVersion) { currentProducts = []; renderProducts(); $('empty').hidden = true; $('trace-panel').hidden = true; showError(error); } }
  finally { if (version === requestVersion) { busy(false); updateVoiceState(); } }
}
async function loadCatalog() {
  const version = ++requestVersion; busy(false); clearError(); $('status').textContent = 'Loading the collection…'; $('trace-panel').hidden = true; $('empty').hidden = true; $('sort').disabled = false; $('sort').value = 'relevance';
  try {
    const selected = filters(); const params = new URLSearchParams(); for (const [key,value] of Object.entries(selected)) if (value !== null) params.set(key,String(value));
    const data = await request('/api/catalog?' + params);
    if (version !== requestVersion) return;
    currentProducts = data.products.map(product => ({product})); renderProducts(); $('status').textContent = `${data.products.length} essentials in this collection`;
  } catch (error) { if (version === requestVersion) showError(error); }
}
function reset() { stopRecording(true); $('query').value = ''; $('filter-category').value = ''; $('filter-min').value = ''; $('filter-max').value = ''; $('filter-stock').checked = false; setMode('text'); loadCatalog(); }
function searchExample(query,category = '') { setMode('text'); $('query').value = query; $('filter-category').value = category; if ($('search').reportValidity()) search(); $('collection').scrollIntoView({behavior:'smooth',block:'start'}); }
function updateVoiceState() {
  if (!voiceReady) return;
  $('voice-state').textContent = recording && recording.state === 'recording' ? 'Listening… press Stop & search when finished.' : 'Ready · English · offline recognition';
}
async function recordVoice() {
  if (recording && recording.state === 'recording') { stopRecording(); return; }
  if (requestingMicrophone) return;
  clearError(); requestingMicrophone = true; $('record').disabled = true;
  const version = ++recordingVersion;
  try {
    if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) throw Error('Microphone recording is unavailable. Open on localhost or HTTPS, or upload an audio file.');
    const stream = await navigator.mediaDevices.getUserMedia({audio:true});
    if (version !== recordingVersion || mode !== 'voice') { stream.getTracks().forEach(t => t.stop()); return; }
    microphoneStream = stream;
    const type = ['audio/webm;codecs=opus','audio/mp4','audio/ogg;codecs=opus'].find(type => MediaRecorder.isTypeSupported(type));
    const recorder = new MediaRecorder(stream,type ? {mimeType:type} : undefined); recording = recorder; const chunks = [];
    recorder.ondataavailable = event => { if (event.data.size) chunks.push(event.data); };
    recorder.onerror = () => { stopRecording(true); showError(Error('Recording failed. Please try again or upload audio.')); };
    recorder.onstop = () => { if (version === recordingVersion && mode === 'voice' && chunks.length) search(new Blob(chunks,{type:recorder.mimeType})); };
    recorder.start(); $('record').classList.add('recording'); $('record').textContent = 'Stop & search'; $('transcript').hidden = true; updateVoiceState();
    recordTimer = setTimeout(() => stopRecording(),12000);
  } catch (error) { stopRecording(true); showError(Error(error.name === 'NotAllowedError' ? 'Microphone permission was denied. Allow access in browser settings or upload audio.' : error.message)); }
  finally { requestingMicrophone = false; $('record').disabled = !voiceReady; }
}
async function initialize() {
  try { catalog = (await request('/api/catalog')).products; renderBag(); } catch (error) { showError(error); }
  await loadCatalog();
  try { const status = await request('/api/voice-status'); voiceReady = status.ready; $('voice-state').textContent = status.message; $('record').disabled = !voiceReady; $('audio-file').disabled = !voiceReady; updateVoiceState(); } catch { $('voice-state').textContent = 'Voice service is unavailable.'; }
}
document.querySelectorAll('[data-mode]').forEach(button => button.onclick = () => setMode(button.dataset.mode));
document.querySelectorAll('[data-query]').forEach(button => button.onclick = () => searchExample(button.dataset.query));
document.querySelectorAll('[data-category]').forEach(button => button.onclick = event => { event.preventDefault(); searchExample(button.dataset.category,button.dataset.category); });
$('orders-link').onclick = () => { $('filter-min').value = ''; $('filter-max').value = ''; searchExample('where is my latest order'); };
$('reset').onclick = $('empty-reset').onclick = reset; $('sort').onchange = renderProducts;
$('apply-filters').onclick = () => {
  if (!$('filter-min').reportValidity() || !$('filter-max').reportValidity()) return;
  if (mode === 'text' && $('query').value.trim()) search();
  else if (mode === 'image' || mode === 'multimodal') { if ($('search').reportValidity()) search(); }
  else loadCatalog();
};
$('image').onchange = () => { if (previewURL) URL.revokeObjectURL(previewURL); const file = $('image').files[0]; $('preview-container').hidden = !file; if (file) { previewURL = URL.createObjectURL(file); $('preview').src = previewURL; } };
$('text-weight').oninput = () => $('weight-label').textContent = Math.round(Number($('text-weight').value)*100) + '%';
$('search').onsubmit = event => { event.preventDefault(); search(); };
$('record').onclick = recordVoice;
$('audio-file').onchange = () => { const file = $('audio-file').files[0]; if (file) { $('transcript').hidden = true; search(file); } };
$('bag-open').onclick = () => { renderBag(); bagModal.show(); };
window.addEventListener('pagehide',() => stopRecording(true));
initialize();
