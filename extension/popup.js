const searchBar = document.getElementById('searchBar');
let groups = [];

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
    setTimeout(function () {
        console.log('ok')
        groups = [
            { name: 'iPhone X', cost: 400, image: 'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-11-pro-select-2019-family?wid=882&amp;hei=1058&amp;fmt=jpeg&amp;qlt=80&amp;op_usm=0.5,0.5&amp;.v=1567812930312' },
            { name: 'bier', cost: 1.50, image: 'data:image/jpeg;base64,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' }
        ]
        displayGroups(groups)
    }, 500)
};

const displayGroups = items => {
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
        <p style="cursor:pointer; color:#CC0000"  class="item-remove" data=${{i:i, id: item.id}}>Remove Item</p>
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
    document.querySelector('#modal-footer').addEventListener('click', ()=>deleteGroup(id))
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

loadCharacters();