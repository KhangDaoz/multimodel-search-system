'use strict';
const $ = id => document.getElementById(id);
let mode = 'text', previewURL = null, currentProducts = [], requestVersion = 0;
const money = value => new Intl.NumberFormat('en-US', {style:'currency', currency:'USD'}).format(value);
const modal = new bootstrap.Modal($('product-modal'));

function element(tag, text = '', className = '') {
  const node = document.createElement(tag);
  node.textContent = text;
  node.className = className;
  return node;
}
async function request(path, options) {
  const response = await fetch(path, options);
  const data = await response.json();
  if (!response.ok) throw Error(data.error || 'Unable to complete this request.');
  return data;
}
function setMode(next) {
  mode = next;
  document.querySelectorAll('[data-mode]').forEach(button => {
    button.classList.toggle('active', button.dataset.mode === mode);
    button.setAttribute('aria-pressed', String(button.dataset.mode === mode));
  });
  $('text-input').hidden = mode === 'image';
  $('image-input').hidden = mode !== 'image';
  $('query').required = mode !== 'image';
  $('image').required = mode === 'image';
  $('query-label').textContent = mode === 'voice' ? 'What did you say? Enter your transcript.' : 'What are you looking for?';
  $('mode-hint').textContent = mode === 'voice' ? 'Voice is simulated: type the words you would say aloud.' : mode === 'image' ? 'PNG, JPEG, or WebP · up to 5 MB. Download a product sample from its details to try it.' : 'Search by colour, category, brand, or a price limit.';
}
function busy(value) {
  $('submit').disabled = value;
  $('spinner').hidden = !value;
  $('submit-label').textContent = value ? 'Searching…' : 'Search ↗';
}
function clearError() { $('error').hidden = true; }
function showError(error) {
  $('error').textContent = error.message;
  $('error').hidden = false;
  $('status').textContent = 'Unable to complete the request.';
}
function imageData(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result.split(',')[1]);
    reader.onerror = () => reject(Error('Cannot read this image.'));
    reader.readAsDataURL(file);
  });
}
async function showDetails(id) {
  try {
    const product = await request('/api/products/' + id);
    $('detail-title').textContent = product.name;
    $('detail-category').textContent = product.category + ' / ' + product.color;
    $('detail-price').textContent = money(product.price);
    $('detail-description').textContent = product.description;
    $('detail-image').src = '/api/product-images/' + product.id;
    $('detail-image').alt = product.name + ' — dataset image';
    $('detail-download').href = '/api/product-images/' + product.id;
    $('detail-download').download = 'product-' + product.id + '.png';
    $('detail-fields').replaceChildren();
    for (const [label, value] of [['Colour', product.color], ['Stock', product.stock ? product.stock + ' available' : 'Out of stock'], ['Product ID', product.id]]) {
      $('detail-fields').append(element('dt', label), element('dd', String(value)));
    }
    modal.show();
  } catch (error) { showError(error); }
}
function renderProducts() {
  $('results').replaceChildren();
  const products = [...currentProducts];
  if ($('sort').value === 'price-low') products.sort((a,b) => a.product.price - b.product.price);
  if ($('sort').value === 'price-high') products.sort((a,b) => b.product.price - a.product.price);
  for (const result of products) {
    const product = result.product;
    const column = element('div', '', 'col-6 col-md-4 col-lg-3');
    const card = element('article', '', 'card product-card');
    const photo = element('div', '', 'product-photo');
    const img = document.createElement('img');
    img.src = '/api/product-images/' + product.id;
    img.alt = product.name + ' — dataset image';
    img.loading = 'lazy';
    photo.append(img);
    if (result.rank) photo.append(element('span', '#' + result.rank + ' MATCH', 'rank-label'));
    if (!product.stock) photo.append(element('span', 'Out of stock', 'stock-badge'));
    const body = element('div', '', 'card-body');
    body.append(element('div', product.category + ' / ' + product.color, 'product-meta'));
    const title = element('div', '', 'product-title-row');
    title.append(element('h3', product.name), element('span', money(product.price), 'product-price'));
    body.append(title);
    if (result.score !== undefined) body.append(element('div', 'Match score · ' + result.score.toFixed(6), 'product-score'));
    const details = element('button', 'View details ↗', 'product-details');
    details.type = 'button';
    details.setAttribute('aria-label', 'View details for ' + product.name);
    details.onclick = () => showDetails(product.id);
    body.append(details); card.append(photo, body); column.append(card); $('results').append(column);
  }
}
function show(response) {
  currentProducts = response.results.map((result,index) => ({...result, rank:index + 1}));
  $('sort').disabled = Boolean(response.order);
  $('empty').hidden = Boolean(response.results.length || response.order);
  $('trace-panel').hidden = false;
  $('trace').textContent = response.processing.join(' → ');
  renderProducts();
  if (response.order) {
    const order = response.order;
    const column = element('div', '', 'col-12 col-lg-8');
    const card = element('article', '', 'card order-card');
    card.append(element('div', 'YOUR ORDER', 'eyebrow'), element('h3', 'Order ' + order.order_id), element('span', order.status, 'badge align-self-start my-3'), element('div', money(order.total), 'detail-price'), element('p', 'Customer ' + order.customer_id + ' · ' + order.date));
    for (const item of order.items || []) card.append(element('div', 'Product #' + item.product_id + ' · Quantity ' + item.quantity + ' · ' + money(item.price) + ' each', 'order-item'));
    column.append(card); $('results').append(column); $('status').textContent = 'Your order details';
  } else $('status').textContent = response.results.length ? `${response.results.length} matches · ${response.candidate_count} products considered` : 'No products or orders found';
}
async function search() {
  const version = ++requestVersion;
  busy(true); clearError(); $('status').textContent = 'Finding your next favourite…';
  try {
    const payload = {mode, query:$('query').value, customer:$('customer').value, top_k:Number($('limit').value)};
    if (mode === 'image') {
      const file = $('image').files[0];
      if (!file) throw Error('Please choose a product image.');
      if (file.size > 5 * 1024 * 1024) throw Error('Please choose an image smaller than 5 MB.');
      payload.image = await imageData(file);
    }
    const response = await request('/api/search', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)});
    if (version === requestVersion) show(response);
  } catch (error) {
    if (version === requestVersion) { currentProducts = []; renderProducts(); $('empty').hidden = true; $('trace-panel').hidden = true; showError(error); }
  } finally { if (version === requestVersion) busy(false); }
}
async function loadCatalog() {
  const version = ++requestVersion;
  busy(false); clearError(); $('status').textContent = 'Loading the collection…';
  $('trace-panel').hidden = true; $('empty').hidden = true; $('sort').disabled = false; $('sort').value = 'relevance';
  try {
    const data = await request('/api/catalog');
    if (version !== requestVersion) return;
    currentProducts = data.products.map(product => ({product}));
    renderProducts(); $('status').textContent = `The full collection · ${data.products.length} essentials`;
  } catch (error) { if (version === requestVersion) showError(error); }
}
function searchExample(query) {
  setMode('text'); $('query').value = query;
  if ($('search').reportValidity()) search();
  $('collection').scrollIntoView({behavior:'smooth', block:'start'});
}
document.querySelectorAll('[data-mode]').forEach(button => button.onclick = () => setMode(button.dataset.mode));
document.querySelectorAll('[data-query]').forEach(button => button.onclick = () => searchExample(button.dataset.query));
document.querySelectorAll('[data-category]').forEach(button => button.onclick = event => {event.preventDefault(); searchExample(button.dataset.category);});
$('orders-link').onclick = () => searchExample('where is my latest order');
$('reset').onclick = $('empty-reset').onclick = () => { $('query').value = ''; loadCatalog(); };
$('sort').onchange = renderProducts;
$('image').onchange = () => {
  if (previewURL) URL.revokeObjectURL(previewURL);
  const file = $('image').files[0]; $('preview-container').hidden = !file;
  if (file) {previewURL = URL.createObjectURL(file); $('preview').src = previewURL;}
};
$('search').onsubmit = event => {event.preventDefault(); search();};
loadCatalog();
