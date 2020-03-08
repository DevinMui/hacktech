const api = new Api()
function getResults() {
    return document.querySelectorAll('ul.srp-results.srp-list.clearfix>li')
}

function waitFor(selector) {
    let time = 2000
    return new Promise(function (res, rej) {
        waitForElementToDisplay(selector, time);
        function waitForElementToDisplay(selector) {
            if (document.querySelector(selector) != null) {
                res(document.querySelector(selector));
            }
            else {
                setTimeout(function () {
                    waitForElementToDisplay(selector, time);
                }, time);
            }
        }
    });
}

console.log('extension active')
if(window.location.href.match(/https?:\/\/www.ebay.com\/itm/)) // product page
    waitFor('.actPanel .u-cb .u-flL').then(afterItemLoad).catch(console.log)
else // search page
    waitFor('ul.srp-results.srp-list.clearfix>li').then(afterSearchLoad).catch(console.log)

function afterItemLoad() {
    addPlusItem(document.querySelector('.actPanel .u-cb .u-flL'))
    document.querySelector('body').appendChild((() => { a = document.createElement('div'); a.className = 'modal'; a.id = 'ex1'; return a })())
}

function afterSearchLoad() {
    let searchResults = getResults()
    searchResults.forEach(i => addPlus(i))
    document.querySelector('body').appendChild((() => { a = document.createElement('div'); a.className = 'modal'; a.id = 'ex1'; return a })())
}

await function addPlusItem(elem) {
    let inside = document.createElement('div')
    inside.style.cssText = 'text-align: right; margin-bottom: 12px; margin-right: 18px'
    inside.innerHTML = (`<div class="btn btn-scnd btn-m vi-VR-btnWdth-L" rel="modal:open" style="margin-right: 20rem; margin-left: 20.102rem; margin-top: 2.0602rem; background: #526Fff; color:white" class="btn">Add to Queue</div>`)
    const itemId = getIdFromUrl(window.location.href)
    inside.childNodes[0].addEventListener('click', () => checkToken((e) => createModal(itemId, e)))
    elem.appendChild(inside)
}

function getIdFromUrl(url) {
    return 'v1' + url.match(/\/([a-zA-Z0-9]+)\?/)[1] + '|0'
}

await function addPlus(elem) {
    let inside = document.createElement('div')
    inside.innerHTML = (`<div rel="modal:open" class="add-to-queue-btn">Add to Queue</div>`)
    const itemId = getIdFromUrl(elem.querySelector('a').href)

    inside.addEventListener('click', () => checkToken((e) => createModal(itemId, e)))
    elem.appendChild(inside)

}

async function getGroupItems(_id) {
    console.log({_id})
    let res =  await api.post('/queue', {_id})
    return await res.json()
}

async function createModal(itemId, email="ebayuser@ebay.com") {
    email = "ebayuser@ebay.com" // we only have the default email
    let res = await api.post('/user', {email})
    res = await res.json()
    let groups = res.queues
    console.log(groups)
    // create layout, onclicks
    // let itemsList = []

    // loads groups into modal
    const title = `
    <div style="text-align:center"><h1 style="margin-top: 0; font-weight: 200; font-size: 24px">
        Add to Queue
    </h1></div>`

    let itemsList = []
    for(let i = 0; i < groups.length; i++) {
        let item = await getGroupItems(groups[i])
        if(item.start) itemsList.push(item)
    }
    const items = itemsList.map((item) => `
    <div class="item-row" data=${item._id} len=${item.orders.length}>
        <h2 class="item-title">${item.name}</h2>
    </div>
    `)
    const footer = `
    <div style="width: 100%; display: flex; cursor:pointer">
        <input class="add-group" input="text" placeholder="Create new group..."></input>
        <input class="add-group" id="max-bid" style="width: 88px; margin-left: 20px" input="text" placeholder="Max bid"></input>
        <span style="font-size: 36px; margin-left: 8px" id="add-plus">+</span>
    </div>
    `
    const outer = `
    <div id="modal-outer">
        ${title}
        ${items.join('')}
        ${footer}
    </div>
    `
    document.querySelector('.modal').innerHTML = outer
    document.querySelectorAll('.item-row').forEach(i => {
        i.addEventListener('click', () => addItem(i.attributes.data.value, itemId, i.attributes.len.value))
    })
    document.querySelector('#add-plus').addEventListener('click', () => {
        // grabs value 
        const name = document.querySelector(".add-group").value
        const maxBid = document.querySelector('#max-bid').value
        // performs add Item
        newGroup(name, maxBid, itemId).then(snackSucc).catch(snackErr('This item is in this group already. Click on the Syrup to find it.'))
    })
    $('#ex1').modal({
        fadeDuration: 250,
        showClose: false
    });
    document.querySelector('.jquery-modal').style['z-index'] = 999 // ebay has some high z-index elems
}

async function removeItem(id) {
    try {
        let r = await api.post('/dequeue_order', {_id:id})
        r = await r.json()
        Snackbar.show({ text: 'Removed from queue.' });
    } catch(e) {
        snackErr()
    }
}

function addItem(qId, _id, len) {
    chrome.storage.sync.get('auth', 
    (i) => {
        api.post('/enqueue_order', 
            {   
                _id: qId, 
                order: {_id}
            })
            .then(r=>r.json())
            .then(() => {
                if(len == 0) {
                    api.post('/start_queue', {
                        user_id: i.auth,
                        queue_id: qId
                    })
                } 
                return true
            })
            .then(() => {$.modal.close(); snackSucc()})
            .catch(snackErr)
    })
    return true
}

function reload() {
    window.location.reload()
}

function snackSucc(e) {
    // start queue
    let w = window.location.reload.bind(window)
    Snackbar.show({ 
        text: 'Successfully added group!', 
        showAction: true, actionText: 'Refresh', 
        pos:'bottom-center', onActionClick: () => reload()
    });
}

function snackErr(e) {
    if(e) return    Snackbar.show({ text: e, pos:'bottom_center' });
    Snackbar.show({ text: 'Please try again later :(' });
}

async function newGroup(name, maxBid, itemId) { // creates a new group
    maxBid = Number.parseFloat(maxBid)
    if(!maxBid) return Snackbar.show({ text: 'Please enter a valid bid' })
    chrome.storage.sync.get(auth, (a) => {
        let r = await api.post('/create_queue', {_id: a.auth, data: {max_bid: maxBid, name: name}})
        r = r.json()
        createModal(itemId)
    })
}

function checkToken(cb) {
    chrome.storage.sync.get('auth', a => {
        if(a) return cb()
        securityFail()
    })
}

function securityFail() {
    chrome.runtime.sendMessage({message: "security fail"}, console.log);
}