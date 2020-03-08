const searchBar = document.getElementById('searchBar');
let groups = [];
const api = Api()
let userId = undefined

searchBar.addEventListener('keyup', (e) => {
    const searchString = e.target.value.toLowerCase();

    const filtered = groups.filter(group => {
        return (
            group.name.toLowerCase().includes(searchString)
        );
    });
    displayGroups(filtered);
});

const loadCharacters = async () => {
    chrome.storage.sync.get('auth', auth)
};

const displayGroups = async auth => {
    let items = []
    // get queus 
    if (items.length == 0) {
        return `      
    <h1>
    <a href="https://www.ebay.com/">No groups match your search <br> Click here to add one!</a>
    </h1>
    `
    }
    const htmlString = items
        .map((item, i) => {
            return `
        <a class="item-row" href="#ex1" rel="modal:open" data=${i}>
            <img src="${item.image}" ></img>
            <h2 class="item-title">${item.name}</h2>
            <h2 class="item-cost"><span style="color: #00AA00; font-weight: 200">Lowest Price: </span>$${Number(item.cost).toFixed(2)}</h2>
        </a>
    `;
        })
        .join('');
    const outer = `<div id="items-list" class="list-card"> 
        ${htmlString}
    </div>`
    document.getElementById('items').innerHTML = outer;
    document.querySelectorAll('.item-row').forEach(item => {
        item.addEventListener('click', () => createModalContents(item.attributes.data.value))
    })
};
let groupItems = {
    0: [{
        id: "1",
        image: 'https://secureir.ebaystatic.com/pictures/aw/pics/stockimage1.jpg',
        name: 'item 1',
        cost: 299
    }, {
        id: "1",
        image: 'https://secureir.ebaystatic.com/pictures/aw/pics/stockimage1.jpg',
        name: 'item 2',
        cost: 350
    }],
    1: [{
        id: "1",
        image: 'https://secureir.ebaystatic.com/pictures/aw/pics/stockimage1.jpg',
        name: 'item 1',
        cost: 299
    }, {
        id: "1",
        image: 'https://secureir.ebaystatic.com/pictures/aw/pics/stockimage1.jpg',
        name: 'item 2',
        cost: 350
    }]
}

function getGroupItems(id) {
    return groupItems[id]
}

function getName(id) {
    return id ? 'one' : 'zero'
}

function createModalContents(id) {
    const title = `<div style="text-align:center"><h1 style="margin-top: 0; font-weight: 200; font-size: 32px">${getName(id)}</h1></div>`
    let itemsList = getGroupItems(id)
    const items = itemsList.map((item, i) => `
<div class="item-row">
    <img src="${item.image}"></img>
    <h2 class="item-title">${item.name}</h2>
    <div class="item-cost">
        <h2>$${Number(item.cost).toFixed(2)}</h2>
        <p style="cursor:pointer; color:#CC0000"  class="item-remove" data=${{ i: i, id: item.id }}>Remove Item</p>
    </div>
</div>
`)
    const footer = `
    <div style="border-top:1px solid #ccc; text-align:center;cursor:pointer"  id="modal-footer" data=${id}>
    <h2 style="color: #CC0000; font-weight: 200; margin-bottom: 0">
        Delete Group
    </h2>
    </div>`
    const outer = `
    <div id="modal-outer">
        ${title}
        ${items}
        ${footer}
    </div>
    `
    console.log(id)
    document.querySelector('.modal').innerHTML = outer
    document.querySelectorAll(".item-remove").forEach(i => {
        i.addEventListener('click', () => {
            removeItem(i.attributes.data.value.i, i.attributes.data.value.id, id)
        })

    })
    document.querySelector('#modal-footer').addEventListener('click', () => deleteGroup(id))
}

function removeItem(i, id, reloadId) {
    groupItems[reloadId] = groupItems[reloadId].splice(i, 1)
    // AJAX to delete item @ reloadId: id
    console.log(groupItems[reloadId])
    createModalContents(reloadId)
}

function deleteGroup(id) {
    // TODO: ajax here
    window.location.reload()
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

loadCharacters();