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
    groups = [{ name: 'iPhone X', cost: 400, image: 'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-11-pro-select-2019-family?wid=882&amp;hei=1058&amp;fmt=jpeg&amp;qlt=80&amp;op_usm=0.5,0.5&amp;.v=1567812930312' }]
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
    .map((item) => {
      return `
        <li class="character">
            <h2>${item.name}</h2>
            <h2>Lowest Cost: $${item.cost}</h2>
            <img src="${item.image}"></img>
        </li>
    `;
    })
    .join('');
  document.getElementById('items').innerHTML = htmlString;
};

loadCharacters();