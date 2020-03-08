// works on ebay search page: https://www.ebay.com/sch/i.html

function getResults() {
    return document.querySelectorAll('ul.srp-results.srp-list.clearfix>li')
    // arr.map(doSomething)
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
    waitFor('.actPanel').then(afterItemLoad).catch(console.log)
else // search page
    waitFor('ul.srp-results.srp-list.clearfix>li').then(afterSearchLoad).catch(console.log)

function afterItemLoad() {
    addPlusItem(document.querySelector('.actPanel'))
    document.querySelector('body').appendChild((() => { a = document.createElement('div'); a.className = 'modal'; a.id = 'ex1'; return a })())
}

function afterSearchLoad() {
    let searchResults = getResults()
    searchResults.forEach(i => addPlus(i))
    document.querySelector('body').appendChild((() => { a = document.createElement('div'); a.className = 'modal'; a.id = 'ex1'; return a })())
}

function addPlusItem(elem) {
    let inside = document.createElement('div')
    inside.style.cssText = 'text-align: right; margin-bottom: 12px; margin-right: 18px'
    inside.innerHTML = (`<div rel="modal:open" style="width: 8.5625rem; background: #526Fff; color:white" class="btn">Add to Queue</div>`)
    // TODO: get itemId
    const itemId = 0
    inside.childNodes[0].addEventListener('click', () => createModal(itemId))
    elem.appendChild(inside)
}


function addPlus(elem) {
    let inside = document.createElement('div')
    inside.innerHTML = (`<div rel="modal:open" class="add-to-queue-btn">Add to Queue</div>`)
    // TODO: get itemId
    const itemId = 0
    inside.addEventListener('click', () => createModal(itemId))
    elem.appendChild(inside)

}

function getGroupItems(group) {
    // returns name given id
    switch (group._id) {
        case "1":
            return {
                "_id": group._id,
                "name": "one",
                "image": "https://i.ebayimg.com/thumbs/images/g/Y~IAAOSwHctbv3Pl/s-l225.webp    "
            }
        case "2":
            return {
                "_id": group._id,
                "name": "two",
                "image": "https://i.ebayimg.com/thumbs/images/g/Y~IAAOSwHctbv3Pl/s-l225.webp    "
            }
    }
}

function createModal(itemId) {
    // if auth fails...
    if(!checkToken()) securityFail()

    // grabs groups (AJAX)
    let groups = [
        { _id: "1" },
        { _id: "2" }
    ]

    // create layout, onclicks
    // loads groups into modal
    const title = `<div style="text-align:center"><h1 style="margin-top: 0; font-weight: 200; font-size: 24px">
        Add to Queue
    </h1></div>`
    let itemsList = groups.map(getGroupItems)
    const items = itemsList.map((item) => `
    <div class="item-row" data=${item._id}>
        <img src="${item.image}"></img>
        <h2 class="item-title">${item.name}</h2>
    </div>
    `)
    const footer = `
    <div style="width: 100%; display: flex; cursor:pointer">
        <input class="add-group" input="text" placeholder="Add to new group..."></input>
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
        i.addEventListener('click', () => addItem(i.attributes.data.value, itemId).then(snackSucc).catch(snackErr))
    })
    document.querySelector('#add-plus').addEventListener('click', () => {
        // grabs value 
        const name = document.querySelector(".add-group").value
        // performs add Item
        newGroup(name, itemId).then(() => {snackSucc(); setTimeout(window.location.reload, 3000)}).catch(snackErr)
    })
    $('#ex1').modal({
        fadeDuration: 250,
        showClose: false
    });
    document.querySelector('.jquery-modal').style['z-index'] = 999 // ebay has some high z-index elems
}

async function removeItem(id) {
    // TODO: make a fetch to remove item
    Snackbar.show({ text: 'Removed from queue.' });
}

async function addItem(id) {
    // TODO: make a fetch
    console.log(id)
    $.modal.close()
    return true
}

function snackSucc(e) {
    console.log(e)
    Snackbar.show({ text: 'Successfully added to group!', showAction: false, pos:'bottom-center' });
}

function snackErr(e) {
    console.log(e)
    Snackbar.show({ text: 'Please try again later :(' });
}

async function newGroup(name, itemId) {
    // TODO: reates a new group with one item in it

}

function checkToken() {
    if(!chrome.storage.sync.get('auth')) return false
    return true
}

function securityFail() {
    // invalidate token
    chrome.storage.sync.set({auth: undefined})
    queryInfo = {active: true};
    chrome.tabs.query(queryInfo, function(result) {
        var activeTab = result[1].id;
        updateProperties = {'url': chrome.extension.getURL('login_page.html'), 'selected': true};
        chrome.tabs.update(activeTab, updateProperties, function() {
            // Anything else you want to do after the tab has been updated.
        });
    });
}
