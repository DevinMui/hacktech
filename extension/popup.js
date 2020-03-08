const searchBar = document.getElementById('searchBar');
let groups = [];
let queueItems = []
const api = new Api()
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
    const email = "ebayuser@ebay.com" // hardcode email for now
    let items = await api.post('/user', {email})
    items = await items.json()
    items = items.queues
    for(let i=0; i < items.length; i++) {
        let epsilon = await api.post('/queue', {_id: items[i]})
        epsilon = await epsilon.json()
        if(epsilon.start) queueItems.push(epsilon)
    }
    displayGroups(queueItems)
};

const displayGroups = async (items) => {
    // get queus 
    if (items.length == 0) {
        return `      
    <h1>
    <a href="https://www.ebay.com/">No groups match your search <br> Click here to add one!</a>
    </h1>
    `
    }
    const htmlString = queueItems
        .map((item) => {
            return `
        <a class="item-row" href="#ex1" rel="modal:open" data=${item._id}>
            <h2 class="item-title">${item.name}</h2>
            <h2 class="item-cost"><span style="color: #00AA00; font-weight: 200">Lowest Price: </span>$${Number(item.max_bid).toFixed(2)}</h2>
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

async function getGroupItems(_id) { 
    let it = [

    ]
    let r = await api.post('/queue', {_id})
    r = await r.json()
    lst = r.orders
    for(let i=0; i< lst.length; i++) {
        let zz = await api.post('/order', {_id:lst[i], itemId:lst[i]})
        zz = await zz.json()
        it.push(zz)
    }
    return it
}

async function getName(_id) {
    let r = await api.post('/queue', {_id})
    r = await r.json()
    return r.name
}

async function createModalContents(id) {
    const title = `<div style="text-align:center"><h1 style="margin-top: 0; font-weight: 200; font-size: 32px">${await getName(id)}</h1></div>`
    let itemsList = await getGroupItems(id)
    const items = itemsList.map((item, i) => `
<div class="item-row">
    <h2 class="item-title">${item.name}</h2>
    <div class="item-cost">
        <h2>$${Number(item.cost).toFixed(2)}</h2>
        <p style="cursor:pointer; color:#CC0000"  class="item-remove" data=${{ i: i, id: item._id }}>Remove Item</p>
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
            removeItem(id,  i.attributes.data.value.id, i.attributes.data.value.i, id)
        })

    })
    document.querySelector('#modal-footer').addEventListener('click', () => deleteGroup(id))
}

function removeItem(qid, oid, reloadId) {
    groupItems[reloadId] = groupItems[reloadId].splice(i, 1)
    // AJAX to delete item @ reloadId: id
    api.post('/remove_order_from_queue', {queue_id: qid, order_id: oid})
    createModalContents(reloadId)
}

async function deleteGroup(_id) {
    await api.post('stop_queue', {_id})
    window.location.reload()
}

loadCharacters();